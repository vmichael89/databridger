from helpers.database import Database
from helpers.sql_query_maker import QueryMaker

# Connect to an SQL database
db_sql = Database.sql(props=dict(
    host="localhost",
    port=5432,
    database="Rockbuster",
    user="postgres",
    password="1234"
))

# Alternatively, connect using CSV data
# db_csv = Database.csv('./path_to_data_directory/')

# Initialize the query maker for the database
qm = QueryMaker(db_sql)

# Usage remains largely the same
df_merged = db_sql.easy_merge({
    "film": ["title", "rental_duration", "rental_rate", "length", "replacement_cost", "rating"],
    "inventory": ["inventory_id"],
    "category": ["name"],
    "payment": ["amount", "payment_date"],
    "rental": ["rental_date", "return_date"],
    "customer": ["customer_id"],
    "city": ["city"],
    "country": ["country"]
})
