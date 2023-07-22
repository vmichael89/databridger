from typing import Dict
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

        self.info = self.get_info()
        self.table_names = self.get_table_names()
        self.tables = self.get_tables()

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

    def get_info(self) -> pd.DataFrame:
        """Fetches information about all columns in the database."""

        return self.query(
            "SELECT * "
            "FROM information_schema.columns"
        )

    def get_table_names(self) -> pd.Series:
        """Fetches a series of unique public table names excluding the views."""

        return self.query(
            "SELECT table_name " 
            "FROM information_schema.columns "
            "WHERE table_schema='public' AND is_updatable='YES'"
        )['table_name'].drop_duplicates()

    def get_tables(self) -> Dict[str, pd.DataFrame]:
        """Fetches all public tables in the database and returns them as a dictionary with their names as keys and
        their content as values in dataframe format."""

        return {table_name: self.query(f"SELECT * FROM {table_name}") for table_name in list(self.table_names)}


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
