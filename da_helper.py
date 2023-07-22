import numpy as np


# Data Cleaning
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
        has_mixed_types = (df[[col]].applymap(type) != df[[col]].iloc[0].apply(type)).any(axis = 1)
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


# Data Wrangling
def create_flag(df, col, flag_col=None, limits=[], labels=[], add_id_col=False):
    """
    Creates a new column 'flag_col' based on the values in the 'col' column.
    Labels are assigned based on the limits specified.
    The 'limits' list must be monotonically increasing.
    If 'flag_col' is not specified, the 'col' column gets overwritten with the flags.

    Parameters:
        df (DataFrame): The input DataFrame where the flag column will be created.
        col (str): The name of the column used to determine the flag values.
        flag_col (str, optional): The name of the new flag column. Defaults to None.
        limits (list, optional): The list of limits defining the intervals for assigning flags. Defaults to [].
        labels (list, optional): The list of labels corresponding to the intervals. Defaults to [].
        add_id_col (bool, optional): Creates another column with the label indices used for sorting.

    Returns:
        None
        
    Raises:
        Exception: If the number of labels is not one more than the number of limits.
        Exception: If the limits list is not monotonically increasing.
    """
    if len(labels) != len(limits) + 1:
        raise Exception("The number of labels must be one more than the number of limits")

    if limits != sorted(limits):
        raise Exception("The limits list must be monotonically increasing")

    limits = [-np.inf, *limits, np.inf]

    if not flag_col:
        flag_col = col

    for i in range(len(labels)):
        df.loc[(df[col] > limits[i]) & (df[col] <= limits[i + 1]), flag_col] = labels[i]
    
    # if add_id_col:
    #    order_mapping = {value: index for index, value in enumerate(labels)}
    #    df[col + "id"] = df.index.map(order_mapping)


# Plotting
def remove_clutter(ax):
    """
    Removes clutter from a matplotlib axes object.

    Parameters:
        ax (Axes): The axes object to remove clutter from.

    Returns:
        None
    """
    
    # Set the x-axis and y-axis labels
    ax.set_xlabel("")
    ax.set_ylabel("")

    # Remove the boundary of the axes
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)

    # Remove the ticks
    ax.tick_params(axis="both", which="both", length=0, labelleft=False)
