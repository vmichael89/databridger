from typing import List, Dict
import psycopg2
import pandas as pd
import pyperclip


class Database:
    """
    Represents a database connection and provides methods to execute SQL queries.

    Attributes:
    - info (pd.DataFrame): DataFrame containing information about all columns in the database.
    - table_names (pd.Series): Series of unique public table names excluding the views.
    - tables (Dict[str, pd.DataFrame]): Dictionary containing table names as keys and corresponding data as pandas DataFrames.
    """

    def __init__(self):
        # Connection properties
        # TODO: use parameters instead of hard coded properties
        self._props = dict(
            host="localhost",
            port=5432,
            database="Rockbuster",
            user="postgres",
            password="1234"
        )

        self.info = self._get_info()
        self.table_names = self._get_table_names()
        self.tables = self._get_tables()
        self.columns_mapping = self._get_mapping()
        self.table_mapping = dict(self.columns_mapping[["from_table", "to_table"]].groupby("from_table")["to_table"].apply(list))

    def query(self, prompt) -> pd.DataFrame:
        """
        Executes a SQL query on the database.

        Parameters:
        - prompt (str): The SQL query to execute.

        Returns:
        - pd.DataFrame: The result of the query as a pandas DataFrame.
        """

        # Establish connection and create cursor to interact with the database
        conn = psycopg2.connect(**self._props)
        cur = conn.cursor()

        # Execute the SQL query
        cur.execute(prompt)

        # Create dataframe from the query result
        rows = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        df = pd.DataFrame(rows, columns=column_names)

        # Close connection
        cur.close()
        conn.close()

        return df

    def _get_info(self) -> pd.DataFrame:
        """Fetches information about all columns in the database."""

        return self.query(
            "SELECT * "
            "FROM information_schema.columns"
        )

    def _get_table_names(self) -> pd.Series:
        """Fetches a series of unique public table names excluding the views."""

        return self.query(
            "SELECT table_name " 
            "FROM information_schema.columns "
            "WHERE table_schema='public' AND is_updatable='YES'"
        )['table_name'].drop_duplicates()

    def _get_tables(self) -> Dict[str, pd.DataFrame]:
        """Fetches all public tables in the database and returns them as a dictionary with their names as keys and
        their content as values in dataframe format."""

        return {table_name: self.query(f"SELECT * FROM {table_name}") for table_name in list(self.table_names)}

    def _get_mapping(self) -> pd.DataFrame:
        """
        Retrieves a DataFrame that maps foreign key relationships between tables in a PostgreSQL database.

        The DataFrame contains four columns: 'from_table', 'from_column', 'to_table', 'to_column'. Each row represents a
        foreign key relationship, where 'from_table' and 'from_column' are the source table and column, and 'to_table'
        and 'to_column' are the target table and column that the source references.

        The function fetches relationships in both directions (from source to target and from target to source). This ensures
        that all relationships are captured, regardless of the direction.

        Only foreign key relationships within the 'public' schema are considered.

        Note: The function relies on system views in the information_schema to fetch the foreign key relationships.

        Returns:
            pd.DataFrame: DataFrame columns_mapping foreign key relationships between tables.
        """

        return self.query(
            "SELECT \n"
            "	A.table_name AS from_table,\n"
            "	A.column_name AS from_column,\n"
            "	B.table_name AS to_table,\n"
            "	B.column_name AS to_column\n"
            "FROM information_schema.key_column_usage A\n"
            "INNER JOIN information_schema.constraint_column_usage B ON A.constraint_name=B.constraint_name\n"
            "INNER JOIN information_schema.table_constraints C ON A.constraint_name=C.constraint_name\n"
            "WHERE A.table_schema = 'public'\n"
            "	AND C.constraint_type = 'FOREIGN KEY'\n"
            "UNION ALL\n"
            "SELECT \n"
            "	B.table_name AS from_table,\n"
            "	B.column_name AS from_column,\n"
            "	A.table_name AS to_table,\n"
            "	A.column_name AS to_column\n"
            "FROM information_schema.key_column_usage A\n"
            "INNER JOIN information_schema.constraint_column_usage B ON A.constraint_name=B.constraint_name\n"
            "INNER JOIN information_schema.table_constraints C ON A.constraint_name=C.constraint_name\n"
            "WHERE A.table_schema = 'public'\n"
            "	AND C.constraint_type = 'FOREIGN KEY'\n"
            "ORDER BY from_table, from_column\n")

    def _get_relationship_path(self, starting_table, ending_table, paths=None):
        """
        Retrieves the shortest path of foreign key relationships between two tables in a PostgreSQL database.

        This function uses depth-first search to traverse the 'table_mapping' graph from 'starting_table' to 'ending_table'.
        The search avoids cycles and upon reaching the 'ending_table', it records the path. After all paths are explored,
        it returns the shortest one.

        Parameters:
        starting_table (str): The name of the starting table in the path.
        ending_table (str): The name of the ending table in the path.
        paths (list, optional): The current path during the recursion. Should not be provided during the initial call.

        Returns:
        list: The shortest path from 'starting_table' to 'ending_table', represented as a list of table names.
              If no path is found, returns None.
        """

        # Initialize paths on first run
        if paths is None:
            paths = [starting_table]

        # Initialize a variable to hold all possible paths
        all_paths = []

        # Go to every possibility from the current table
        for next_table in self.table_mapping[starting_table]:

            # If next_table is the target, we have found a path!
            if next_table == ending_table:
                all_paths.append(paths + [next_table])

            # Don't go where you already have been
            elif next_table not in paths:
                # Rerun with next table
                all_paths.extend(self._get_relationship_path(next_table, ending_table, paths + [next_table]))

        # If this is the top level of recursion, find and return the shortest path
        if paths == [starting_table]:
            if not all_paths:
                return None
            return min(all_paths, key=len)

        # If this is not the top level of recursion, just return all paths
        else:
            return all_paths

    def _get_multi_rel_path(self, list_of_tables) -> List[List]:
        # init first path
        sub_paths = [self._get_relationship_path(*list_of_tables[:2])]

        # iterate over rest of tables in list
        for table in list_of_tables[2:]:
            distinct_tables = set(element for sublist in sub_paths for element in sublist)
            next_sub_path = min([db._get_relationship_path(s, table) for s in distinct_tables], key=len)
            sub_paths.append(next_sub_path)

        return sub_paths

    def _get_merge_sequence_from_path(self, multi_relationship_path) -> List[List]:
        sequence = []
        for sub_path in multi_relationship_path:
            for left_table, right_table in zip(sub_path[:-1], sub_path[1:]):
                next_mapping = self.columns_mapping[(self.columns_mapping["from_table"] == left_table) & (self.columns_mapping["to_table"] == right_table)]
                if len(next_mapping) == 1:
                    sequence.append(next_mapping.values.tolist()[0])
                else:
                    raise Exception(f"No mapping found between {left_table} and {right_table}")
        return sequence

    def easy_merge(self, selected_columns_by_table) -> pd.DataFrame:
        """
        Merges multiple tables based on shortest relationship paths and returns selected columns from each table.

        This function uses the `get_relationship_path` method to determine the shortest path
        from 'table1' to 'table3' and then the shortest connection from that path to 'table6'.
        Using these paths, the function then identifies the relationships (primary and foreign keys)
        between the tables. It then merges all tables based on these keys, forming a large DataFrame.
        From this DataFrame, it selects and returns the columns specified by the user.

        Parameters:
        selected_columns_by_table (dict): A dictionary where each key is a table name (str) and each
        value is a list of column names (str) of interest from that table.
        Example: {'table1': ['col1', 'col2'], 'table3': ['col1'], 'table6': ['col2', 'col5', 'col6']}
        """
        multi_path = self._get_multi_rel_path(list(selected_columns_by_table.keys()))
        merge_sequence = self._get_merge_sequence_from_path(multi_path)

        df = None
        for from_table, from_column, to_table, to_column in merge_sequence:
            df1 = self.tables[from_table].copy()
            df1.columns = [f"{from_table}_" + col for col in df1.columns]
            df2 = self.tables[to_table].copy()
            df2.columns = [f"{to_table}_" + col for col in df2.columns]

            if df is None:
                df = pd.merge(df1, df2, left_on=f"{from_table}_{from_column}", right_on=f"{to_table}_{to_column}")
            else:
                df = pd.merge(df, df2, left_on=f"{from_table}_{from_column}", right_on=f"{to_table}_{to_column}")

        columns_to_extract = [f"{key}_{val}" for key, val_list in selected_columns_by_table.items() for val in val_list]

        return df[columns_to_extract]


class QueryMaker:
    """
    Represents a QueryMaker object that interacts with the Database to generate SQL queries for specific tasks.

    Attributes:
    - db (Database): The Database object to interact with the database.
    """

    def __init__(self, database):
        self.db = database

    def profile(self, table, to_clipboard=False):
        """Generates a query to profile data for a specific table. The profile includes the column name, number of
        missing values, number of duplicated values, number of distinct values, and the distinct values.

        Parameters:
        - table (str): The name of the table to profile.
        - to_clipboard (bool, optional): If True, the query will be copied to the clipboard.
                                         Defaults to False.
        """

        # Generate the query
        q = ("".join([(f"\n"
                       f"SELECT \n"
                       f"    '{col}' AS column,\n"
                       f"  SUM(CASE WHEN {col} IS NULL THEN 1 ELSE 0 END) AS missing,\n"
                       f"	SUM(CASE WHEN {col} IS NOT NULL THEN 1 ELSE 0 END) - COUNT(DISTINCT {col}) AS duplicated,\n"
                       f"    COUNT(DISTINCT {col}) AS distinct,\n"
                       f"	STRING_AGG(DISTINCT {col}::text, ', ') AS distinct_values\n"
                       f"FROM {table}\n"
                       f"UNION ALL") for col in self.db.tables[table].columns]))

        # remove last UNION ALL
        q = "\n".join(q.split("\n")[:-1])

        # Print or copy to clipboard
        if to_clipboard:
            pyperclip.copy(q)
            print("Copied SQL code to clipboard.")
        else:
            print(q)

    def statistics(self, table, toclip=False):
        """Generates a query to summarize descriptive statistics for a specific table. The statistics includes the
        minimum, maximum, average, mode and the number of values.

        Parameters:
        - table (str): The name of the table to profile.
        - to_clipboard (bool, optional): If True, the query will be copied to the clipboard.
                                         Defaults to False.
        """

        # Get a list of numeric columns; non-numeric columns need to be treated differently
        numeric_columns = self.db.tables[table].select_dtypes(include='number').columns

        # Generate the query
        # Only calculate statistics for numeric columns.
        # Mode is type casted to VARCHAR to allow mixed types
        q = ("".join([(f"\n"
                       f"SELECT \n"
                       f"    '{col}' AS column,\n"
                       f"    {f'MIN({col})' if col in numeric_columns else 'NULL'},\n"
                       f"    {f'MAX({col})' if col in numeric_columns else 'NULL'},\n"
                       f"    {f'AVG({col})' if col in numeric_columns else 'NULL'},\n"
                       f"    (SELECT MODE() WITHIN GROUP (ORDER BY {col}))::VARCHAR,\n"
                       f"    COUNT({col}),\n"
                       f"    COUNT(*) AS count_rows\n"
                       f"FROM {table}\n"
                       f"UNION ALL")
                      for col in self.db.tables[table].columns]))

        # Remove last UNION ALL
        q = "\n".join(q.split("\n")[:-1])

        # Print or copy to clipboard
        if toclip:
            pyperclip.copy(q)
        else:
            print(q)


if __name__ == "__main__":
    # Connect to database Rockbuster (examine db to look into the database)
    db = Database()

    # Initialize the querymaker for the database
    qm = QueryMaker(db)

    # Copy query strings insertable into RDBMS / get possible table_names from db.table_names
    # qm.profile(table_name, to_clipboard=True)
    # qm.statistics(table_name, to_clipboard=True)

    df_merged = db.easy_merge({
        "film": ["title", "rental_duration"],
        "category": ["name"],
        "payment": ["amount"],
        "customer": ["customer_id"],
        "city": ["city"],
        "country": ["country"]})
