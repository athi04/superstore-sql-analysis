"""
Cleans and normalises the real Sample Superstore dataset (9,994 rows) into a
relational schema: customers, products, orders, order_items.

This is a REAL, widely-used retail dataset (source: github.com/Ayon-coder/FUTURE_ML_01,
originally the Tableau/Kaggle Sample Superstore dataset), not synthetic data.
It arrives largely clean, but it is a single flat table, not a relational database,
and it has one genuine data quality issue worth fixing: some Product IDs map to
more than one Product Name (naming drift over time / re-listed products).
"""

import pandas as pd

import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "data", "raw", "superstore.csv")
CLEAN = os.path.join(BASE, "data", "clean")
os.makedirs(CLEAN, exist_ok=True)

df = pd.read_csv(RAW, encoding="ISO-8859-1")

# Parse dates (source format is M/D/YYYY)
df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")
df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%m/%d/%Y")

# ---------- PRODUCTS ----------
# Real issue: 32 Product IDs have more than one Product Name recorded.
# Resolve by taking the most frequently used name per Product ID.
name_counts = df.groupby(["Product ID", "Product Name"]).size().reset_index(name="n")
canonical_names = (
    name_counts.sort_values("n", ascending=False)
    .drop_duplicates(subset="Product ID")
    [["Product ID", "Product Name"]]
)
inconsistent_ids = name_counts.groupby("Product ID").size()
n_inconsistent = (inconsistent_ids > 1).sum()
print(f"Products: resolved {n_inconsistent} Product IDs that had inconsistent names")

products = (
    df[["Product ID", "Category", "Sub-Category"]]
    .drop_duplicates(subset="Product ID")
    .merge(canonical_names, on="Product ID")
    .rename(columns={
        "Product ID": "product_id", "Category": "category",
        "Sub-Category": "sub_category", "Product Name": "product_name",
    })
)
products.to_csv(f"{CLEAN}/products.csv", index=False)

# ---------- CUSTOMERS ----------
customers = (
    df[["Customer ID", "Customer Name", "Segment"]]
    .drop_duplicates(subset="Customer ID")
    .rename(columns={
        "Customer ID": "customer_id", "Customer Name": "customer_name", "Segment": "segment",
    })
)
customers.to_csv(f"{CLEAN}/customers.csv", index=False)

# ---------- ORDERS ----------
# One order can appear on multiple rows (one per line item) but shares order-level
# fields (dates, ship mode, customer, ship-to location) -- take the first occurrence.
orders = (
    df[["Order ID", "Order Date", "Ship Date", "Ship Mode", "Customer ID",
        "Country", "City", "State", "Postal Code", "Region"]]
    .drop_duplicates(subset="Order ID")
    .rename(columns={
        "Order ID": "order_id", "Order Date": "order_date", "Ship Date": "ship_date",
        "Ship Mode": "ship_mode", "Customer ID": "customer_id", "Country": "country",
        "City": "city", "State": "state", "Postal Code": "postal_code", "Region": "region",
    })
)
orders.to_csv(f"{CLEAN}/orders.csv", index=False)

# ---------- ORDER ITEMS ----------
order_items = df[["Row ID", "Order ID", "Product ID", "Sales", "Quantity", "Discount", "Profit"]].rename(
    columns={
        "Row ID": "order_item_id", "Order ID": "order_id", "Product ID": "product_id",
        "Sales": "sales", "Quantity": "quantity", "Discount": "discount", "Profit": "profit",
    }
)
order_items.to_csv(f"{CLEAN}/order_items.csv", index=False)

print("\nClean relational tables written to", CLEAN)
print(f"  customers.csv    -> {len(customers)} rows")
print(f"  products.csv     -> {len(products)} rows")
print(f"  orders.csv       -> {len(orders)} rows")
print(f"  order_items.csv  -> {len(order_items)} rows")
