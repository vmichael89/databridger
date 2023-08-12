# DataBridger

DataBridger is a Python library meticulously crafted to bridge the journey from raw, unprocessed data to meaningful 
insights for data analysts and scientists. Whether you're ingesting data from sources like CSV files or SQL databases, 
or delving into the intricate tasks of cleaning, wrangling, and visualizing, DataBridger serves as your comprehensive 
pathway to insights.

Well, at least one day. DataBridger is still at the beginning of its development :D

## Features

- **Data Loading and Interaction**: 
  - PostgreSQL
    - send queries
    - construct query strings for various purposes and copy it to clipboard
  - CSV file base
  

- **Data Cleaning**: 
  - Run checks for mixed data types, missing values, and duplicates.
  

- **Data Wrangling**: 
  - create flag columns
  

- **Visualization Helpers**: Simplify and beautify your data plots.

<br>

**Coming soon**

| Feature              | Description                                                                                                |
|----------------------|------------------------------------------------------------------------------------------------------------|
| (issue_tracker)      | Helps in documenting analysis process (cleaning, exploration, etc.)                                        |
| (sql_query_export)   | Export SQL queries to Excel (already used in a script of another project)                                  |
| (erd)                | Generate ERD (already used in a script of another project)                                                 |
| (key_identification) | Better identification of inter-table relationships (primary/foreign keys) without relying on equal namings |
| (easier_merge)       | Making easy merge easier in terms providing column names. Add an 'merge_all' option                        |

## Installation

`git clone https://github.com/vmichael89/databridger.git`


## Quick Start

Run simple check on your DataFrame
```python
import databridger.analysis as da
da.clean.check_types(df)
da.clean.check_duplicates(df)
```

Connect to CSV database
```python
from databridger import Database

db_csv = Database.csv('./path_to_data_directory/')
```

Inspect tables

```db_csv.tables```

Connect to SQL database
```python
from databridger import Database

db_sql = Database("dbname=database_name user=postgres password=your_password host=localhost port=5432", "postgres")
```
Construct queries for simple profiling and statistics

```python
from databridger import Database
from databridger import QueryMaker

db_sql = Database("dbname=database_name user=postgres password=your_password host=localhost port=5432", "postgres")
qm = QueryMaker(db_sql)

print(qm.profile("customer"))  # also saves to clipboard

```
## Documentation

coming soon

## Testing

Tests are located in the `tests/` directory. Use the following command to run tests:

TODO

## Contributing

Open for contributions.

## License

MIT

## Contact

For any inquiries or issues, please open an issue on GitHub or contact me at [vyndellmichael@gmail.com](mailto:vyndellmichael@gmail.com).
