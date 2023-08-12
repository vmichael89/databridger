import numpy as np


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
