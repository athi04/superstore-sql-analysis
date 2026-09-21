import sqlite3
import pandas as pd

import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN = os.path.join(BASE, "data", "clean")
DB = os.path.join(BASE, "retail.db")

conn = sqlite3.connect(DB)

pd.read_csv(f"{CLEAN}/customers.csv").to_sql("customers", conn, if_exists="replace", index=False)
pd.read_csv(f"{CLEAN}/products.csv").to_sql("products", conn, if_exists="replace", index=False)
pd.read_csv(f"{CLEAN}/orders.csv").to_sql("orders", conn, if_exists="replace", index=False)
pd.read_csv(f"{CLEAN}/order_items.csv").to_sql("order_items", conn, if_exists="replace", index=False)

conn.execute("CREATE INDEX idx_orders_customer ON orders(customer_id)")
conn.execute("CREATE INDEX idx_items_order ON order_items(order_id)")
conn.execute("CREATE INDEX idx_items_product ON order_items(product_id)")
conn.commit()
conn.close()
print(f"Database built at {DB}")
