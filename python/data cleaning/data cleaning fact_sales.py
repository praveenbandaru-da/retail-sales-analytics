"""
================================================================================
DATA CLEANING SCRIPT FOR fact_sales.csv
================================================================================
This script performs comprehensive data cleaning on the fact_sales dataset,
including handling missing order_date values using the deterministic 7-day
shipping business rule.

Author: Data Analyst
Date: 2026-07-03
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# STEP 1: LOAD THE DATA
# =============================================================================

# Load the raw CSV file
df = pd.read_csv(r'C:\Users\ramub\Desktop\sql-data-analytics-project\sql-data-analytics-project\datasets\flat-files\fact_sales.csv')

print("=" * 70)
print("STEP 1: LOAD THE DATA")
print("=" * 70)
print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")
print(f"Columns: {list(df.columns)}")
print(f"\nData Types:\n{df.dtypes}")
print(f"\nFirst 5 rows:\n{df.head()}")

# =============================================================================
# STEP 2: INITIAL DATA QUALITY ASSESSMENT
# =============================================================================

print("\n" + "=" * 70)
print("STEP 2: INITIAL DATA QUALITY ASSESSMENT")
print("=" * 70)

# 2.1 Check for missing values
print("\n--- 2.1 Missing Values ---")
missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(2)
missing_df = pd.DataFrame({'Missing Count': missing, 'Missing %': missing_pct})
print(missing_df)

# 2.2 Check for empty/whitespace strings in object columns
print("\n--- 2.2 Empty/Whitespace Strings ---")
for col in df.select_dtypes(include=['object']).columns:
    empty_count = (df[col].astype(str).str.strip() == '').sum()
    print(f"  {col}: {empty_count} empty/whitespace strings")

# 2.3 Check for duplicate rows
print("\n--- 2.3 Duplicate Rows ---")
print(f"Exact duplicate rows: {df.duplicated().sum()}")
print(f"Duplicates on (order_number, product_key): {df.duplicated(subset=['order_number', 'product_key']).sum()}")

# 2.4 Basic statistics for numeric columns
print("\n--- 2.4 Numeric Column Statistics ---")
print(df[['sales_amount', 'quantity', 'price']].describe())

# =============================================================================
# STEP 3: VERIFY THE DETERMINISTIC SHIPPING RULE
# =============================================================================

print("\n" + "=" * 70)
print("STEP 3: VERIFY THE DETERMINISTIC SHIPPING RULE")
print("=" * 70)

# Work with rows that have valid order_date to verify the business rule
df_valid = df[df['order_date'].notna()].copy()
df_valid['order_date_dt'] = pd.to_datetime(df_valid['order_date'])
df_valid['shipping_date_dt'] = pd.to_datetime(df_valid['shipping_date'])
df_valid['due_date_dt'] = pd.to_datetime(df_valid['due_date'])

# Calculate date gaps
df_valid['order_to_shipping'] = (df_valid['shipping_date_dt'] - df_valid['order_date_dt']).dt.days
df_valid['shipping_to_due'] = (df_valid['due_date_dt'] - df_valid['shipping_date_dt']).dt.days
df_valid['order_to_due'] = (df_valid['due_date_dt'] - df_valid['order_date_dt']).dt.days

print("\nOrder -> Shipping gap (days):")
print(df_valid['order_to_shipping'].describe())
print(f"Unique values: {sorted(df_valid['order_to_shipping'].unique())}")

print("\nShipping -> Due gap (days):")
print(df_valid['shipping_to_due'].describe())
print(f"Unique values: {sorted(df_valid['shipping_to_due'].unique())}")

print("\nOrder -> Due gap (days):")
print(df_valid['order_to_due'].describe())
print(f"Unique values: {sorted(df_valid['order_to_due'].unique())}")

print("\n✅ CONFIRMED: Order→Shipping = 7 days, Shipping→Due = 5 days (deterministic rule)")

# =============================================================================
# STEP 4: INSPECT MISSING order_date ROWS
# =============================================================================

print("\n" + "=" * 70)
print("STEP 4: INSPECT MISSING order_date ROWS")
print("=" * 70)

missing_order_date = df[df['order_date'].isnull()]
print(f"Rows with missing order_date: {len(missing_order_date)}")
print(f"\nAll missing order_date rows:\n")
print(missing_order_date.to_string())

# =============================================================================
# STEP 5: DATA CLEANING - CONVERT DATA TYPES
# =============================================================================

print("\n" + "=" * 70)
print("STEP 5: CONVERT DATA TYPES")
print("=" * 70)

# Create a working copy for cleaning
df_clean = df.copy()

# Convert date columns to datetime (coerce errors to NaT)
df_clean['order_date'] = pd.to_datetime(df_clean['order_date'], errors='coerce')
df_clean['shipping_date'] = pd.to_datetime(df_clean['shipping_date'], errors='coerce')
df_clean['due_date'] = pd.to_datetime(df_clean['due_date'], errors='coerce')

print("Date columns converted to datetime.")
print(f"  order_date: {df_clean['order_date'].dtype}")
print(f"  shipping_date: {df_clean['shipping_date'].dtype}")
print(f"  due_date: {df_clean['due_date'].dtype}")

# =============================================================================
# STEP 6: IMPUTE MISSING order_date VALUES
# =============================================================================

print("\n" + "=" * 70)
print("STEP 6: IMPUTE MISSING order_date VALUES")
print("=" * 70)

# Count missing values before imputation
missing_before = df_clean['order_date'].isnull().sum()
print(f"Missing order_date BEFORE imputation: {missing_before}")

# Apply the deterministic business rule:
# order_date = shipping_date - 7 days
missing_mask = df_clean['order_date'].isnull()
df_clean.loc[missing_mask, 'order_date'] = df_clean.loc[missing_mask, 'shipping_date'] - pd.Timedelta(days=7)

# Count missing values after imputation
missing_after = df_clean['order_date'].isnull().sum()
print(f"Missing order_date AFTER imputation: {missing_after}")
print(f"Rows successfully imputed: {missing_before - missing_after}")

# Verify the imputation
print("\n--- Verification of Imputed Values ---")
imputed_rows = df_clean.iloc[missing_mask[missing_mask].index].copy()
imputed_rows['order_to_shipping'] = (imputed_rows['shipping_date'] - imputed_rows['order_date']).dt.days
print(imputed_rows[['order_number', 'order_date', 'shipping_date', 'due_date', 'order_to_shipping']].head(10))
print(f"\nAll imputed order->shipping gaps: {sorted(imputed_rows['order_to_shipping'].unique())}")

# =============================================================================
# STEP 7: POST-CLEANING DATA VALIDATION
# =============================================================================

print("\n" + "=" * 70)
print("STEP 7: POST-CLEANING DATA VALIDATION")
print("=" * 70)

# 7.1 Verify no missing values remain
print("\n--- 7.1 Missing Values After Cleaning ---")
print(df_clean.isnull().sum())

# 7.2 Verify date consistency across ALL rows
print("\n--- 7.2 Date Consistency Check ---")
df_clean['order_to_shipping'] = (df_clean['shipping_date'] - df_clean['order_date']).dt.days
df_clean['shipping_to_due'] = (df_clean['due_date'] - df_clean['shipping_date']).dt.days
df_clean['order_to_due'] = (df_clean['due_date'] - df_clean['order_date']).dt.days

invalid_shipping = (df_clean['order_to_shipping'] != 7).sum()
invalid_due = (df_clean['shipping_to_due'] != 5).sum()
print(f"Rows where order->shipping != 7 days: {invalid_shipping}")
print(f"Rows where shipping->due != 5 days: {invalid_due}")

# 7.3 Verify sales_amount = quantity * price
print("\n--- 7.3 Sales Amount Consistency ---")
df_clean['calculated_amount'] = df_clean['quantity'] * df_clean['price']
df_clean['amount_diff'] = df_clean['sales_amount'] - df_clean['calculated_amount']
inconsistent = (df_clean['amount_diff'] != 0).sum()
print(f"Rows where sales_amount != quantity * price: {inconsistent}")
if inconsistent > 0:
    print(df_clean[df_clean['amount_diff'] != 0][['order_number', 'product_key', 'sales_amount', 'quantity', 'price', 'calculated_amount', 'amount_diff']].head())

# 7.4 Check for negative or zero values
print("\n--- 7.4 Negative/Zero Values ---")
for col in ['sales_amount', 'quantity', 'price']:
    neg = (df_clean[col] < 0).sum()
    zero = (df_clean[col] == 0).sum()
    print(f"  {col}: {neg} negative, {zero} zero values")

# 7.5 Check date ranges
print("\n--- 7.5 Date Ranges ---")
print(f"Order date range: {df_clean['order_date'].min()} to {df_clean['order_date'].max()}")
print(f"Shipping date range: {df_clean['shipping_date'].min()} to {df_clean['shipping_date'].max()}")
print(f"Due date range: {df_clean['due_date'].min()} to {df_clean['due_date'].max()}")

# 7.6 Check for duplicates
print("\n--- 7.6 Duplicate Check ---")
print(f"Exact duplicate rows: {df_clean.duplicated().sum()}")
print(f"Duplicates on (order_number, product_key): {df_clean.duplicated(subset=['order_number', 'product_key']).sum()}")

# =============================================================================
# STEP 8: CLEANED DATA SUMMARY
# =============================================================================

print("\n" + "=" * 70)
print("STEP 8: CLEANED DATA SUMMARY")
print("=" * 70)

print(f"\nTotal rows: {len(df_clean)}")
print(f"Total columns: {len(df_clean.columns)}")
print(f"Date range: {df_clean['order_date'].min().date()} to {df_clean['order_date'].max().date()}")
print(f"Unique orders: {df_clean['order_number'].nunique()}")
print(f"Unique products: {df_clean['product_key'].nunique()}")
print(f"Unique customers: {df_clean['customer_key'].nunique()}")
print(f"Total revenue: ${df_clean['sales_amount'].sum():,.2f}")
print(f"Average order value: ${df_clean.groupby('order_number')['sales_amount'].sum().mean():.2f}")

print("\n--- Numeric Summary ---")
print(df_clean[['sales_amount', 'quantity', 'price']].describe())

# =============================================================================
# STEP 9: SAVE CLEANED DATA
# =============================================================================

print("\n" + "=" * 70)
print("STEP 9: SAVE CLEANED DATA")
print("=" * 70)

# Drop helper columns before saving
columns_to_drop = ['calculated_amount', 'amount_diff', 'order_to_shipping', 'shipping_to_due', 'order_to_due']
for col in columns_to_drop:
    if col in df_clean.columns:
        df_clean.drop(columns=[col], inplace=True)

# Save to CSV
output_path = r'C:\Users\ramub\Desktop\sales-analytics-project\data\cleaned\fact_sales_cleaned.csv'
df_clean.to_csv(output_path, index=False)
print(f"\n✅ Cleaned data saved to: {output_path}")
print(f"   File size: {len(df_clean)} rows x {len(df_clean.columns)} columns")

print("\n" + "=" * 70)
print("DATA CLEANING COMPLETE!")
print("=" * 70)