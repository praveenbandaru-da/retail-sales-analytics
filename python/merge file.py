"""
merge_files.py
Retail Sales Analytics Project

Combines the three cleaned star-schema tables (dim_customers,
dim_products, fact_sales) into a single flat/merged table for
convenience in Python/Excel-style analysis.

Note: This merged file is for ad-hoc analysis convenience only.
Tableau, Power BI, and SSMS should continue using the three
separate tables with relationships/joins (star schema) - merging
them permanently would duplicate customer/product attributes
across every line item and bloat file size unnecessarily.
"""
import pandas as pd

CLEAN_DIR = r"C:\Users\ramub\Desktop\sales-analytics-project\data\cleaned"

# ---------- Load the three cleaned tables ----------
customers = pd.read_csv(f"{CLEAN_DIR}/dim_customers_cleaned.csv")
products = pd.read_csv(f"{CLEAN_DIR}/dim_products_cleaned.csv")
sales = pd.read_csv(f"{CLEAN_DIR}/fact_sales_cleaned.csv")

print(f"dim_customers_cleaned: {customers.shape[0]:,} rows")
print(f"dim_products_cleaned:  {products.shape[0]:,} rows")
print(f"fact_sales_cleaned:    {sales.shape[0]:,} rows")

# ---------- Merge: fact_sales is the base table (LEFT JOIN) ----------
# LEFT JOIN keeps every sales transaction even if a dimension lookup
# were ever missing - protects against silently dropping revenue rows.
merged = (
    sales
    .merge(customers, on="customer_key", how="left")
    .merge(products, on="product_key", how="left")
)

# ---------- Validation ----------
assert len(merged) == len(sales), (
    "Row count changed after merge - check for duplicate keys in a dimension table."
)
print(f"\nMerged table: {merged.shape[0]:,} rows, {merged.shape[1]} columns")

missing_cust = merged['first_name'].isnull().sum()
missing_prod = merged['product_name'].isnull().sum()
print(f"Rows with no matching customer: {missing_cust}")
print(f"Rows with no matching product:  {missing_prod}")

# ---------- Save ----------
output_path = f"{CLEAN_DIR}/merged_flat_table.csv"
merged.to_csv(output_path, index=False)
print(f"\nSaved merged table to: {output_path}")