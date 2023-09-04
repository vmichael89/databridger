import databridger
db = databridger.Database(r"C:\Users\vynde\Documents\GitHub\brazilian-ecommerce-olist\data\raw")
db.update_columns_mapping(["geolocation_zip_code_prefix"])
db.create_erd(attr_kwargs=dict(nodesep="2", ranksep="2"), node_kwargs=dict(fontname="Helvetica"))
