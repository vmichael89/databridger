from abc import ABC, abstractmethodfrom typing import List, Dictfrom pathlib import Pathimport psycopg2import pandas as pdfrom graphviz import Digraphclass DataStrategy(ABC):    """    Abstract base class defining the interface for data handling strategies.    This class provides an outline for operations required to interact with different    types of data sources, such as CSV files or SQL databases. Concrete implementations    of this interface will provide specific strategies for loading data and retrieving    mappings or relationships between data tables.    """    @abstractmethod    def load_data(self) -> Dict[str, pd.DataFrame]:        """        Load data from source to a dictionary of DataFrames representing the tables."""        pass    @abstractmethod    def get_mapping(self, tables=None):        """        Infer relationships or mappings between tables.        This method attempts to infer relationships based on common columns or specific        naming conventions in the tables.        Parameters:            tables (dict): Dictionary containing loaded data tables from CSV files.                           Keys are inferred names of the CSV files and values are the                           corresponding pandas DataFrames.        Returns:            pd.DataFrame: DataFrame capturing the inferred relationships between CSV tables.                          Structure might include 'from_table', 'from_column', 'to_table',                          and 'to_column' to denote the relationships.        """        passclass CSVStrategy(DataStrategy):    """Concrete strategy implementation for handling CSV data sources."""    def __init__(self, source):        self.source = source    def load_data(self) -> Dict[str, pd.DataFrame]:        """Load data from the specified CSV source."""        tables = {}        for csv_file in Path(self.source).glob('*.csv'):            dataset_name = str(csv_file.stem)            tables[dataset_name] = pd.read_csv(csv_file)        return tables    def get_mapping(self, tables) -> pd.DataFrame:        ssr_threshold = 0.95        potential_primary_keys = [            (table, column)            for table in tables.keys()            for column in tables[table].columns            if tables[table][column].is_unique]        # All columns are potential foreign keys        potential_foreign_keys = [            (table, column)            for table in tables.keys()            for column in tables[table].columns]        # Init column mapping dataframe        columns = ["from_table", "from_column", "to_table", "to_column", "subset_ratio"]        df_column_mapping = pd.DataFrame(columns=columns)        # Loop over potential primary keys and foreign keys        for tab_a, col_a in potential_primary_keys:            for tab_b, col_b in potential_foreign_keys:                # Don't compare one column to itself                if (tab_a, col_a) != (tab_b, col_b):                    # Calculate subset ratio                    ssr = self._compute_subset_ratio(tables[tab_a][col_a], tables[tab_b][col_b])                    # If it is above the threshold, add the connection                    if ssr >= ssr_threshold:                        values = [tab_b, col_b, tab_a, col_a, ssr]                        new_df_row = pd.DataFrame([dict(zip(columns, values))])                        df_column_mapping = pd.concat([df_column_mapping, new_df_row], ignore_index=True)        return df_column_mapping    @staticmethod    def _compute_subset_ratio(from_column, to_column):        from_set = set(from_column.dropna())        to_set = set(to_column.dropna())        # Number of matching entries        matching_entries = len(from_set.intersection(to_set))        # Total unique entries in both columns        total_entries = len(to_set)        return matching_entries / total_entries if total_entries != 0 else 0    def get_mapping_by_names(self, tables) -> pd.DataFrame:        """Infer relationships or mappings between different CSV files based on common column naming."""        from_tables = []        from_columns = []        to_tables = []        to_columns = []        for key in tables:            for column in tables[key].columns:                # if column.endswith("_id"):                for potential_key in tables:                    if column in tables[potential_key].columns and key != potential_key:                        # If a common column is found in another table, store the relationship details                        from_tables.append(key)                        from_columns.append(column)                        to_tables.append(potential_key)                        to_columns.append(column)        return pd.DataFrame({            'from_table': from_tables,            'from_column': from_columns,            'to_table': to_tables,            'to_column': to_columns        })class SQLStrategy(DataStrategy):    """Concrete strategy implementation for handling SQL database data sources."""    def __init__(self, source, db_type):        self.source = source        self.db_type = db_type        self._props = self._parse_source(source)    def _parse_source(self, source):        """Parses the connection string to extract connection properties."""        props = {}        parameters = source.split()        for param in parameters:            key, value = param.split('=')            props[key] = value        return props    def load_data(self):        """Fetch data from the specified SQL source."""        table_names = self.query(            "SELECT table_name "             "FROM information_schema.columns "            "WHERE table_schema='public' AND is_updatable='YES'"        )['table_name'].drop_duplicates()        return {table_name: self.query(f"SELECT * FROM {table_name}") for table_name in list(table_names)}    def get_mapping(self, tables=None):        """Retrieve relationships or mappings (e.g., foreign keys) between different tables in the SQL database."""        return self.query(            "SELECT \n"            "	A.table_name AS from_table,\n"            "	A.column_name AS from_column,\n"            "	B.table_name AS to_table,\n"            "	B.column_name AS to_column\n"            "FROM information_schema.key_column_usage A\n"            "INNER JOIN information_schema.constraint_column_usage B ON A.constraint_name=B.constraint_name\n"            "INNER JOIN information_schema.table_constraints C ON A.constraint_name=C.constraint_name\n"            "WHERE A.table_schema = 'public'\n"            "	AND C.constraint_type = 'FOREIGN KEY'\n"            "UNION ALL\n"            "SELECT \n"            "	B.table_name AS from_table,\n"            "	B.column_name AS from_column,\n"            "	A.table_name AS to_table,\n"            "	A.column_name AS to_column\n"            "FROM information_schema.key_column_usage A\n"            "INNER JOIN information_schema.constraint_column_usage B ON A.constraint_name=B.constraint_name\n"            "INNER JOIN information_schema.table_constraints C ON A.constraint_name=C.constraint_name\n"            "WHERE A.table_schema = 'public'\n"            "	AND C.constraint_type = 'FOREIGN KEY'\n"            "ORDER BY from_table, from_column\n")    def get_info(self) -> pd.DataFrame:        """Fetches information about all columns in the database."""        return self.query(            "SELECT * "            "FROM information_schema.columns"        )    def query(self, prompt) -> pd.DataFrame:        """        Executes a SQL query on the database.        Parameters:            prompt (str): The SQL query to execute.        Returns:            pd.DataFrame: The result of the query as a pandas DataFrame.        """        # Establish connection and create cursor to interact with the database        conn = psycopg2.connect(**self._props)        cur = conn.cursor()        # Execute the SQL query        cur.execute(prompt)        # Create dataframe from the query result        rows = cur.fetchall()        column_names = [desc[0] for desc in cur.description]        df = pd.DataFrame(rows, columns=column_names)        # Close connection        cur.close()        conn.close()        return dfclass Database:    """    Provides an interface to interact with data sources, supporting both CSV and SQL databases.    The class abstracts the specifics of the data source by using a strategy pattern.    Depending on the provided source and database type, it delegates operations to    either a CSVStrategy or an SQLStrategy.    Attributes:        strategy (DataStrategy): The strategy object (CSVStrategy or SQLStrategy)                                 responsible for handling specific data operations.        tables (dict): Dictionary containing loaded data tables. The keys are table names                       and the values are pandas DataFrames.        columns_mapping (pd.DataFrame): DataFrame capturing relationships (e.g., foreign key mappings)                                         between tables, if applicable.    Usage:        For CSV:        db = Database("/path/to/csv_directory/")        For SQL (e.g., PostgreSQL):        db = Database("dbname=mydatabase user=myuser password=mypassword host=localhost port=5432", db_type="postgres")    """    def __init__(self, source, db_type=None):        """        Initialize the Database class with a specific data source and, if needed, a database type.        Parameters:            source (str): Path for CSVs or connection string/details for SQL databases.            db_type (str, optional): Type of the SQL database (e.g., "postgres"). Not required for CSV sources.        """        if Path(source).exists():            self.strategy = CSVStrategy(source)        elif db_type:  # Assuming this is an SQL database            self.strategy = SQLStrategy(source, db_type)        else:            raise ValueError("Invalid source or database type.")        self.tables = self.strategy.load_data()        self.columns_mapping = self.strategy.get_mapping(self.tables)        self.table_mapping = dict(self.columns_mapping[["from_table", "to_table"]].groupby("from_table")["to_table"].apply(list))        self.info = self.get_info()    def get_info(self):        all_table_column_pairs = [            (table, column)            for table in self.tables.keys()            for column in self.tables[table].columns        ]        foreign_keys = self.columns_mapping[["from_table", "from_column"]].to_numpy().tolist()        primary_keys = self.columns_mapping[["to_table", "to_column"]].to_numpy().tolist()        summary = []        for table, column in all_table_column_pairs:            series = self.tables[table][column]            # Initialize dictionary, later used as a dataframe row            data = {"table": table, "column": column}            # Common summary statistics for all types            data["count"] = len(series)            unique_count = series.nunique()            data["unique_count"] = unique_count            data["duplicated_count"] = len(series) - series.drop_duplicates().size            data["missing_values"] = series.isna().sum()            # Determine if the column is a key            if ([table, column] in primary_keys) and ([table, column] in foreign_keys):                # lazy import                from fuzzywuzzy import process                # Key is unique in more than 1 table. Its membership is determined by name                data["type"] = "key"                # Get the table with the highest similarity score for the current column                best_match_table, best_match_score = process.extractOne(column, self.tables.keys())                # If the current table has the highest similarity score, it's primary; otherwise, it's foreign                if table == best_match_table:                    data["subtype"] = "primary"                else:                    data["subtype"] = "foreign"            elif ([table, column] in primary_keys):                data["type"] = "key"                data["subtype"] = "primary"            elif ([table, column] in foreign_keys):                data["type"] = "key"                data["subtype"] = "foreign"            elif (series.is_unique):                data["type"] = "key"                data["subtype"] = "internal"            elif "_id" in column:                data["type"] = "key"                data["subtype"] = "unknown"            # Determine if the column is temporal            elif pd.api.types.is_datetime64_any_dtype(series):                data["type"] = "temporal"                if series.dt.time.nunique() == 1:  # Only the date varies                    data["subtype"] = "date"                elif series.dt.date.nunique() == 1:  # Only the time varies                    data["subtype"] = "time"                else:                    data["subtype"] = "datetime"                # summary statistics                data["min_date"] = series.min()                data["max_date"] = series.max()                data["range"] = series.max() - series.min()            # Determine if column is some sort of spatial data            elif any([kw in series.name.lower() for kw in                      ['latitude', 'longitude', 'lat', 'long', 'lng', 'geo', 'coordinates']]):                data["type"] = "spatial"                data["subtype"] = "coordinates"            elif any([kw in series.name.lower() for kw in                      ['address', 'city', 'state', 'zipcode', 'zip_code', 'postcode', 'country', 'region', 'district',                       'location']]):                data["type"] = "spatial"                data["subtype"] = "region"            # Determine if the column is numeric            elif pd.api.types.is_numeric_dtype(series):                data["type"] = "numeric"                if pd.api.types.is_integer_dtype(series) or (                        pd.api.types.is_float_dtype(series) and series.dropna().apply(float.is_integer).all()):                    data["subtype"] = "discrete"                elif pd.api.types.is_float_dtype(series):                    data["subtype"] = "continuous"                else:                    data["subtype"] = "unknown"                # summary statistics                data["min"] = series.min()                data["max"] = series.max()                data["mean"] = series.mean()            # Determine if the column is text_            # - is a object type (string)            # - more than 10 unique counts            elif (pd.api.types.is_object_dtype(series) and unique_count > 10):                data["type"] = "text"                data["subtype"] = "free-text"                # summary statistics                mode_data = series.mode()                data["mode"] = mode_data[0] if not mode_data.empty else None                data["mode_count"] = (series == data["mode"]).sum()            # Determine if the column is categorical:            # - other object types            elif pd.api.types.is_object_dtype(series):                data["type"] = "categorical"                data["subtype"] = "nominal"                # summary statistics                mode_data = series.mode()                data["mode"] = mode_data[0] if not mode_data.empty else None                data["mode_count"] = (series == data["mode"]).sum()            else:                data["type"] = "unknown"                data["subtype"] = "unknown"            # Append the computed metrics for the column to the summary list            summary.append(data)        return pd.DataFrame(summary)    def _get_relationship_path(self, starting_table, ending_table, paths=None):        """        Retrieves the shortest path of foreign key relationships between two tables in a PostgreSQL database.        This function uses depth-first search to traverse the 'table_mapping' graph from 'starting_table' to 'ending_table'.        The search avoids cycles and upon reaching the 'ending_table', it records the path. After all paths are explored,        it returns the shortest one.        Parameters:            starting_table (str): The name of the starting table in the path.            ending_table (str): The name of the ending table in the path.            paths (list, optional): The current path during the recursion. Should not be provided during the initial call.        Returns:            list: The shortest path from 'starting_table' to 'ending_table', represented as a list of table names.                  If no path is found, returns None.        """        # Initialize paths on first run        if paths is None:            paths = [starting_table]        # Initialize a variable to hold all possible paths        all_paths = []        # Go to every possibility from the current table        for next_table in self.table_mapping[starting_table]:            # If next_table is the target, we have found a path!            if next_table == ending_table:                all_paths.append(paths + [next_table])            # Don't go where you already have been            elif next_table not in paths:                # Rerun with next table                all_paths.extend(self._get_relationship_path(next_table, ending_table, paths + [next_table]))        # If this is the top level of recursion, find and return the shortest path        if paths == [starting_table]:            if not all_paths:                return None            return min(all_paths, key=len)        # If this is not the top level of recursion, just return all paths        else:            return all_paths    def _get_multi_rel_path(self, list_of_tables) -> List[List]:        """        Determine the shortest paths of relationships between a list of tables.        The method starts by determining the shortest relationship path between the        first two tables in the provided list. It then iteratively finds the shortest        paths between previously found tables and the next table in the list.        Parameters:            list_of_tables (List[str]): A list of table names for which to find relationship paths.        Returns:            List[List]: A list containing the shortest relationship paths between the provided tables.                        Each relationship path is represented as a list of table names.        """        # init first path        sub_paths = [self._get_relationship_path(*list_of_tables[:2])]        # iterate over rest of tables in list        for table in list_of_tables[2:]:            distinct_tables = set(element for sublist in sub_paths for element in sublist)            # don't get next sub_path if table is already satisfied in distinct_tables            if table not in distinct_tables:                next_sub_path = min([self._get_relationship_path(s, table) for s in distinct_tables], key=len)                sub_paths.append(next_sub_path)        return sub_paths    def _get_merge_sequence_from_path(self, multi_relationship_path) -> List[List]:        """        Extract merge sequences based on the relationship paths.        For each relationship path provided, this method determines the tables        and columns that should be used to merge or join the tables together.        It leverages the columns_mapping attribute to identify the right relationships.        Parameters:           multi_relationship_path (List[List]): A list containing relationship paths                                                between tables, where each path is represented                                                as a list of table names.        Returns:           List[List]: A list representing the merge sequence. Each element of the list                       contains information about the 'from_table', 'from_column',                       'to_table', and 'to_column' that should be used for merging.        Raises:           Exception: If no mapping is found between two tables in the relationship path        """        sequence = []        for sub_path in multi_relationship_path:            for left_table, right_table in zip(sub_path[:-1], sub_path[1:]):                next_mapping = self.columns_mapping[(self.columns_mapping["from_table"] == left_table) & (                            self.columns_mapping["to_table"] == right_table)]                if len(next_mapping) == 1:                    sequence.append(next_mapping.values.tolist()[0])                else:                    raise Exception(f"No mapping found between {left_table} and {right_table}")        return sequence    def easy_merge(self, selected_columns_by_table) -> pd.DataFrame:        """        Merges multiple tables based on shortest relationship paths and returns selected columns from each table.        This function uses the `get_relationship_path` method to determine the shortest path        from 'table1' to 'table3' and then the shortest connection from that path to 'table6'.        Using these paths, the function then identifies the relationships (primary and foreign keys)        between the tables. It then merges all tables based on these keys, forming a large DataFrame.        From this DataFrame, it selects and returns the columns specified by the user.        Parameters:            selected_columns_by_table (dict): A dictionary where each key is a table name (str) and each value is a                                              list of column names (str) of interest from that table.        Example:            db.easy_merge({'table1': ['col1', 'col2'], 'table3': ['col1'], 'table6': ['col2', 'col5', 'col6']})        """        multi_path = self._get_multi_rel_path(list(selected_columns_by_table.keys()))        merge_sequence = self._get_merge_sequence_from_path(multi_path)        df = None        for from_table, from_column, to_table, to_column in merge_sequence:            df1 = self.tables[from_table].copy()            df1.columns = [f"{from_table}_" + col for col in df1.columns]            df2 = self.tables[to_table].copy()            df2.columns = [f"{to_table}_" + col for col in df2.columns]            if df is None:                print(f"{from_table} shape: {df1.shape}")                df = pd.merge(df1, df2, left_on=f"{from_table}_{from_column}", right_on=f"{to_table}_{to_column}")                print(f"{to_table} shape: {df2.shape} --> MERGED shape: {df.shape}")            else:                df = pd.merge(df, df2, left_on=f"{from_table}_{from_column}", right_on=f"{to_table}_{to_column}")                print(f"{to_table} shape: {df2.shape} --> MERGED shape: {df.shape}")            # TODO: Performance issue with large datasets. Only keep columns of interest.            # catch error            if any(["_x" in c for c in df.columns]) & any(["_y" in c for c in df.columns]):                print("PROBLEM. TABLE PAIR MERGED 2nd TIME")        columns_to_extract = [f"{key}_{val}" for key, val_list in selected_columns_by_table.items() for val in val_list]        return df[columns_to_extract]    def create_erd(self, attr_kwargs={}, node_kwargs={}, edge_kwargs={}, render_kwargs={}):        dot = Digraph('ERD')        # Create nodes for each table        for table, df in self.tables.items():            # Split columns into keys and other columns based on the 'info' DataFrame            foreign_keys = self.columns_mapping[["from_table", "from_column"]].to_numpy().tolist()            primary_keys = self.columns_mapping[["to_table", "to_column"]].to_numpy().tolist()            keys = [col for col in df.columns if [table, col] in [*foreign_keys, *primary_keys]]            columns = [col for col in df.columns if col not in keys]            # Create the label with the desired format            key_rows = ''.join(['<tr> <td port="{}" align="left">+ {}</td> </tr>'.format(key, key) for key in keys])            if key_rows:                key_rows = f'<table border="0" cellborder="0" cellspacing="0" > {key_rows} </table>'            column_rows = ''.join(['<tr> <td port="{}" align="left">- {}</td> </tr>'.format(col, col) for col in columns])            if column_rows:                column_rows = f'<table border="0" cellborder="0" cellspacing="0" > {column_rows} </table>'            label = '''<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">                                <tr> <td> <b>{}</b> </td> </tr>                                <tr> <td> {} </td> </tr>                                <tr> <td> {} </td> </tr>                            </table>>'''.format(table, key_rows, column_rows)            dot.node(table, label, shape='record', **node_kwargs)        # Create edges based on the column_mapping        for idx, row in self.columns_mapping.iterrows():            dot.edge(row['from_table'] + ':' + row['from_column'], row['to_table'] + ':' + row['to_column'], **edge_kwargs)        dot.attr(**attr_kwargs)        # Return or save the rendered ERD        dot.render('erd.gv', view=True, **render_kwargs)