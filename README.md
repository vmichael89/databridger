# DataBridger

DataBridger is a Python library designed to assist data analysts and scientists throughout every stage of the data analysis process. From loading data, whether it's from a CSV or SQL database, to cleaning, wrangling, and visualization, DataBridger has got you covered.

## Features

- **Unified Data Loading**: Load data seamlessly from CSV files or SQL databases.
  
- **Database Interactions**: Provides an interface to interact with SQL databases, execute queries, and fetch structured data.
  
- **Data Cleaning**: Functions to check for mixed data types, missing values, and duplicates in your data.
  
- **Data Wrangling**: Tools to reshape, transform, and merge data to make it analysis-ready.
  
- **Visualization Helpers**: Simplify and beautify your data plots.

## Installation

`pip install databridger`


## Quick Start

Here's a basic guide to get you started:

```python
from databridger import Database
# Load data from SQL database
db = Database.sql(props={...})
# Load data from CSV directory
db_csv = Database.csv('./path_to_data_directory/')

# (Include more examples that cover the main functionalities of the library.)
```
## Documentation

coming soon

## Testing

Tests are located in the `tests/` directory. Use the following command to run tests:

```bash
python -m unittest discover tests
```

## Contributing

(If you're open to contributions, provide some guidance on how someone can contribute. Mention coding standards, PR process, etc.)

## License

MIT

## Contact

For any inquiries or issues, please [open an issue on GitHub](link-to-repo) or contact us at [vyndellmichael@gmail.com](mailto:vyndellmichael@gmail.com).
