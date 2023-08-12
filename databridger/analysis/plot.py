import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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