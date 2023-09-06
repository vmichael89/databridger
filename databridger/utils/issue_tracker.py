from datetime import datetime
import pandas as pd


class CustomDataFrame(pd.DataFrame):
    """Subclass of pandas DataFrame with custom formatting capabilities.

    Features:
    - Provides a custom 'formatted' property that returns a styled version of
      the DataFrame with custom formatting.
    - Ensures that operations on the CustomDataFrame will return a new instance
      of CustomDataFrame, rather than a basic pandas DataFrame.
    """

    FORMAT_LINE_BREAK = {
        'description': lambda x: str(x).replace("\n", "<br>"),
        'notes': lambda x: str(x).replace("\n", "<br>"),
        'relevant_data': lambda x: str(x).replace("\n", "<br>")}

    @property
    def formatted(self):
        """Returns a styled version of the DataFrame where specific columns
        have their newlines replaced with HTML line breaks."""
        return self.style.format(self.FORMAT_LINE_BREAK)

    @property
    def _constructor(self):
        """Ensures that any operations that return a new DataFrame instance
        (like slicing, querying, etc.) will return an instance of CustomDataFrame
        instead of a basic pandas DataFrame. This is important to ensure that
        the methods and properties we've defined in our subclass are available
        in the resulting DataFrame objects."""
        return CustomDataFrame

    def __finalize__(self, other, method=None, **kwargs):
        """This method is a part of pandas' inheritance mechanism and is called
        whenever a new object is created as a result of some operation.
        By overriding this method and calling the parent class's `__finalize__`,
        we can ensure that any custom attributes or methods are properly carried
        over to the new object."""
        return super().__finalize__(other, method=method, **kwargs)


class IssueTracker:
    """
    IssueTracker: A simple class for managing, tracking and documenting issues during data exploration and cleaning.

    The `IssueTracker` provides methods to add new issues, update existing ones,
    and manage their resolution process. It captures important details about an issue,
    such as its description, severity, potential cause, data relevant to the issue,
    and additional notes.

    Attributes:
        df (pd.DataFrame): A DataFrame holding all the issue information.
        issue_count (int): A counter for the issues added.

    Private Attributes:
        _VALID_FIELDS (List[str]): Fields that are allowed to be changed in the issue tracker.
        _FORMAT_LINE_BREAK (Dict[str, Callable]): Formatting dictionary used for rendering the HTML representation of the DataFrame.

    Methods:
        show(): Returns a styled DataFrame for displaying in Jupyter.
        show_latest_versions(): Returns the latest versions of each issue.
        add_issue(...): Adds a new issue to the tracker.
        update_issue(...): Updates the details of an existing issue.
        resolve_issue(...): Marks an issue as resolved.
        export_to_csv(...): Exports the issues to a CSV file.

    Example:
        # Create an instance of IssueTracker
        tracker = IssueTracker()

        # Adding and updating issues
        tracker.add_issue(
            description="duplicated key values",
            severity="minor",
            relevant_data="customers -> customer_unique_id"
        )
        tracker.update_issue(notes="Data quality seems compromised due to duplicate entries.")

    Note:
        The tracker is designed for simplicity and may need extensions or modifications for more advanced use cases.
        It assumes a linear progression of issue versions and doesn't account for branching version histories.
    """

    VALID_FIELDS = ["description", "resolution", "potential_cause", "relevant_data", "notes"]

    def __init__(self):
        self.df = pd.DataFrame(columns=["issue_id", "version", "status", *self.VALID_FIELDS])
        self.issue_count = 0

    def __repr__(self):
        return self.df.__repr__()

    def _repr_html_(self):
        return self.df._repr_html_()

    def show(self):
        """Display the DataFrame with custom formatting."""
        return CustomDataFrame(self.df)

    def show_latest_versions(self):
        """Display the latest versions of issues."""
        return CustomDataFrame(self.df.groupby("issue_id").last())

    def add_issue(self, description, relevant_data, potential_cause=None, notes=None):
        """Add a new issue to the tracker."""

        issue = {
            "issue_id": self.issue_count + 1,
            "version": 1,
            "status": "Open",
            "description": description,
            "resolution": None,
            "potential_cause": potential_cause,
            "relevant_data": relevant_data,
            "notes": notes
        }
        self.df = pd.concat([self.df, pd.DataFrame([issue])], ignore_index=True)

        self.issue_count += 1

        issue_str = f'Issue.{issue["issue_id"]}.{issue["version"]}'
        descr_str = issue["description"]
        reldata_str = issue["relevant_data"].replace("\n", " and ")
        print("---\n")
        print(f'{issue_str} ({descr_str})')
        print(f'Data: {reldata_str}')
        if issue["potential_cause"]:
            print("\n---\n")
            print(f'Potential cause: {issue["potential_cause"]}')
        if notes:
            print("\n---\n")
            print(f'{notes}')
        print("\n---\n")

    def update_issue(self, /, status=None, description=None, potential_cause=None, relevant_data=None, notes=None,
                     issue_id=None, resolution=None):
        """Update an existing issue. If no issue ID is provided, the last issue will be updated."""

        if issue_id is None:
            issue = self.df.iloc[-1]
        else:
            issue = self.df.loc[self.df["issue_id"] == issue_id, :].iloc[-1]

        new_issue = issue.copy()

        new_issue["version"] = issue["version"] + 1

        if (new_issue["status"] == "resolved") and (issue["issue_id"] == new_issue["issue_id"]):
            raise Exception("Issue already resolved.")

        # Apply the updates
        if status is not None:
            new_issue["status"] = status
        if description is not None:
            new_issue["description"] = description
        if potential_cause is not None:
            new_issue["potential_cause"] = potential_cause
        if relevant_data is not None:
            new_issue["relevant_data"] = relevant_data
        if resolution is not None:
            new_issue["resolution"] = resolution

        # overwrite notes always
        new_issue["notes"] = notes

        self.df = pd.concat([self.df, pd.DataFrame([new_issue])])

        issue_str = f'Issue.{new_issue["issue_id"]}.{new_issue["version"]}'
        descr_str = new_issue["description"]
        reldata_str = new_issue["relevant_data"].replace("\n", " and ")
        print("---\n")
        print(f'{issue_str} ({descr_str})')
        print(f'Data: {reldata_str}')
        if new_issue["potential_cause"]:
            print("\n---\n")
            print(f'Potential cause: {new_issue["potential_cause"]}')
        if notes:
            print("\n---\n")
            print(f'{notes}')
        print("\n---\n")

    def resolve_issue(self, resolution, issue_id=None):
        """Mark an issue as resolved."""

        if not issue_id:
            issue_id = self.issue_count

        self.update_issue(status="resolved", resolution=resolution, issue_id=issue_id)

        print(f"Resolved: {resolution}")

    def export_to_csv(self, filename="issues.csv"):
        """Export the issues data to a CSV file."""

        self.df.to_csv(filename, index=False)
