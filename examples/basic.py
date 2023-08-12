from databridger import Database
from databridger import QueryMaker

# Connect to an SQL database
db_sql = Database("dbname=Rockbuster user=postgres password=1234 host=localhost port=5432", "postgres")
# also copies to clipboard

# Querymaker example
qm = QueryMaker(db_sql)
print()
print(qm.profile("customer"))

# Example of easy merge
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

# Read CSV database
raw_data_folder = r"C:\Users\vynde\Documents\GitHub\brazilian-ecommerce-olist\data\raw"
db_csv = Database(raw_data_folder)  # content stored in db_csv.tables
print()
print(db_csv.table_mapping)


