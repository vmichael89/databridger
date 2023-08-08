import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


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

def remove_clutter(ax=None):
    """
    Removes clutter from an axes object.

    Parameters:
        ax (Axes): The axes object to remove clutter from.

    Returns:
        None
    """

    if not ax:
        ax = plt.gca()

    # Set the x-axis and y-axis labels
    ax.set_xlabel("")
    ax.set_ylabel("")

    # Remove the boundary of the axes
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)

    # Remove the ticks
    ax.tick_params(axis="both", which="both", length=0, labelleft=False, labelbottom=False, labelright=False)


def multibar(data, x, y, nsections=None, xorder=None, yorder="sum", title=None, bar_dict=dict(), line_dict=dict()):
    """creates a horizontal bar plot with multiple bars for each category in the 'y' column. It uses the  pd.crosstab  function to create a cross-tabulation of the data. Here is a breakdown of the function:

    Parameters:
    -  data : The input DataFrame.
    -  x : The column name representing the different sections of the bars.
    -  y : The column name representing the categories for which bars are created.
    -  nsections  (optional): The number of sections separated by vertical lines. If not provided, it is calculated based on the number of columns in the cross-tabulation plus one.
    -  xorder  (optional): A list of section names in the desired order. The function finds the best match in the columns to determine the order.
    -  yorder  (optional): The order in which categories are sorted. By default, it sorts rows from highest sum across columns to lowest.
    -  title  (optional): The title of the plot.
    -  bar_dict  (optional): A dictionary of keyword arguments to customize the appearance of the bars.
    -  line_dict  (optional): A dictionary of keyword arguments to customize the appearance of the vertical lines.

    Returns:
        None
    """

    cross_tab = pd.crosstab(data[y], data[x])

    # number of sections separated by vertical lines
    if not nsections:
        nbars = len(cross_tab.columns) + 1

    if xorder:
        # find the best match in the columns to determine the order
        idices = [[el.lower() in col.lower() for col in cross_tab.columns].index(True) for el in xorder]
        col_order = [cross_tab.columns[idx] for idx in idices]
        cross_tab = cross_tab[col_order]

    # sort rows from highest sum across columns to lowest
    if yorder == "sum":
        cross_tab = cross_tab.loc[cross_tab.sum(axis=1).sort_values(ascending=True).index]  # sort by sum of all

    # normalize vertically (by y)
    cross_tab = cross_tab.div(cross_tab.sum(axis=0), axis=1)

    # normalize horizontally (by x)
    cross_tab = cross_tab.div(cross_tab.sum(axis=1), axis=0) * 100

    # Plot
    axs = cross_tab.plot(kind='barh', subplots=True, layout=(1, 3), sharex=False, legend=False)

    # l = ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    # l.set_title(None)
    for ax in axs:
        remove_clutter()

    # plt.tick_params(labelleft=True, labelbottom=True, labelsize=12)
    # ticks = np.linspace(0, 100, nbars)
    # labels = [f"{l:.0f}%" for l in ticks]
    # plt.xticks(ticks, labels);

    if title:
        plt.title(title, fontsize=15)

    # for tick in ticks:
    #    plt.plot([tick, tick], plt.ylim(), "--", color="#303030", linewidth=1, **line_dict)


def bar100(data, x, y, nsections=None, xorder=None, yorder="sum", title=None, bar_dict=dict(), line_dict=dict()):
    """creates a stacked horizontal bar plot where each bar represents 100% of the category. It uses the  pd.crosstab  function to create a cross-tabulation of the data. Here is a breakdown of the function:

    Parameters:
    -  data : The input DataFrame.
    -  x : The column name representing the different sections of the bars.
    -  y : The column name representing the categories for which bars are created.
    -  nsections  (optional): The number of sections separated by vertical lines. If not provided, it is calculated based on the number of columns in the cross-tabulation plus one.
    -  xorder  (optional): A list of section names in the desired order. The function finds the best match in the columns to determine the order.
    -  yorder  (optional): The order in which categories are sorted. By default, it sorts rows from highest sum across columns to lowest.
    -  title  (optional): The title of the plot.
    -  bar_dict  (optional): A dictionary of keyword arguments to customize the appearance of the bars.
    -  line_dict  (optional): A dictionary of keyword arguments to customize the appearance of the vertical lines.

    Returns:
        None
    """

    cross_tab = pd.crosstab(data[y], data[x])

    # number of sections separated by vertical lines
    if not nsections:
        nbars = len(cross_tab.columns) + 1

    if xorder:
        # find the best match in the columns to determine the order
        idices = [[el.lower() in col.lower() for col in cross_tab.columns].index(True) for el in xorder]
        col_order = [cross_tab.columns[idx] for idx in idices]
        cross_tab = cross_tab[col_order]

    # sort rows from highest sum across columns to lowest
    if yorder == "sum":
        cross_tab = cross_tab.loc[cross_tab.sum(axis=1).sort_values(ascending=True).index]  # sort by sum of all

    # normalize vertically (by y)
    cross_tab = cross_tab.div(cross_tab.sum(axis=0), axis=1)

    # normalize horizontally (by x)
    cross_tab = cross_tab.div(cross_tab.sum(axis=1), axis=0) * 100

    # Plot
    ax = cross_tab.plot.barh(stacked=True, width=0.8, **bar_dict)

    l = ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    l.set_title(None)

    remove_clutter()
    plt.tick_params(labelleft=True, labelbottom=True, labelsize=12)
    ticks = np.linspace(0, 100, nbars)
    labels = [f"{l:.0f}%" for l in ticks]
    plt.xticks(ticks, labels);

    if title:
        plt.title(title, fontsize=15)

    for tick in ticks:
        plt.plot([tick, tick], plt.ylim(), "--", color="#303030", linewidth=1, **line_dict)