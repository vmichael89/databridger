import pyperclip


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
        # Mode is type cast to VARCHAR to allow mixed types
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
