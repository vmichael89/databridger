def check_types(df):
    """
    Checks for columns with mixed data types in the DataFrame.
    Prints the names of columns that have mixed types.

    Parameters:
        df (DataFrame): The input DataFrame to check for mixed data types.

    Returns:
        None
    """
    print("Columns with mixed types:")
    for col in df.columns.tolist():
        has_mixed_types = (df[[col]].applymap(type) != df[[col]].iloc[0].apply(type)).any(axis=1)
        print(f"  {col}: {'YES' if len(df[has_mixed_types]) > 0 else 'no'}")


def check_missing(df):
    """
    Checks for missing values in the DataFrame.
    Prints the number of missing values for each column.
    Returns a dictionary with DataFrames containing NaN values for inspection.

    Parameters:
        df (DataFrame): The input DataFrame to check for missing values.

    Returns:
        dict: A dictionary containing DataFrames with NaN values for each column.
    """
    print("Missing values:")
    df_nan = {}  # Dictionary to store DataFrames with NaN values
    for col in df.columns.tolist():
        has_missing_values = df[col].isnull()  # Boolean mask to identify missing values
        num_missing = sum(has_missing_values)  # Count the number of missing values
        df_nan[col] = df[has_missing_values]  # Store DataFrame with missing values
        print(f"  {col}: {num_missing}")  # Print the column name and number of missing values
    return df_nan


def check_duplicates(df, subset=None):
    """
    Checks for duplicate records and values in the DataFrame.
    Prints the number of true duplicates and the number of duplicates for each column.
    If a subset is provided, it checks for duplicates based on that subset of columns.

    Parameters:
        df (DataFrame): The input DataFrame to check for duplicates.
        subset (list, optional): A list of column names to consider for duplicate checking. Defaults to None.

    Returns:
        None
    """
    num_true_dups = df.duplicated().sum()  # Count the number of true duplicates
    print(f"Number of true duplicates: {num_true_dups}")

    print("Duplicate values:")
    for col in df.columns.tolist():
        num_dups = df.duplicated(subset=[col]).sum()  # Count the number of duplicates for each column
        print(f"  {col}: {num_dups}")

    if subset:
        num_sub_dups = df.duplicated(subset=subset).sum()  # Count the number of duplicates for the specified subset
        print(f"Number of duplicates for subset {subset}: {num_sub_dups}")