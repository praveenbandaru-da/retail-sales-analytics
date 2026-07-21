"""
Phase 5 - Exploratory Data Analysis
Retail Sales Analytics Project

Loads the cleaned star-schema tables, builds a merged flat table for
convenience, and produces summary statistics + 8 charts covering
distribution, univariate, multivariate, trend, and segment analysis.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

plt.rcParams.update({'figure.dpi': 110, 'font.size': 10,
                      'axes.spines.top': False, 'axes.spines.right': False})

CLEAN = r"C:\Users\ramub\Desktop\sales-analytics-project\data\cleaned"
CHARTS = r"C:\Users\ramub\Desktop\sales-analytics-project\reports"

cust = pd.read_csv(f"{CLEAN}/dim_customers_cleaned.csv", parse_dates=['birthdate', 'create_date'])
prod = pd.read_csv(f"{CLEAN}/dim_products_cleaned.csv", parse_dates=['start_date'])
sales = pd.read_csv(f"{CLEAN}/fact_sales_cleaned.csv", parse_dates=['order_date', 'shipping_date', 'due_date'])

# ---------- Build the merged flat table (for EDA convenience only) ----------
df = sales.merge(cust, on='customer_key', how='left').merge(prod, on='product_key', how='left')
df.to_csv(f"{CLEAN}/merged_flat_table.csv", index=False)

# Derived fields
df['order_month'] = df['order_date'].dt.to_period('M').astype(str)
df['age'] = (pd.Timestamp.today() - df['birthdate']).dt.days / 365.25
df['age_group'] = pd.cut(df['age'], bins=[0, 25, 35, 45, 55, 65, 150],
                          labels=['<25', '25-34', '35-44', '45-54', '55-64', '65+'])
df['margin'] = df['sales_amount'] - df['cost']

# =========== 1. SUMMARY STATISTICS ===========
print("=== SUMMARY STATISTICS ===")
print(df[['sales_amount', 'quantity', 'price', 'cost']].describe().round(2))
print("\nSkewness:")
print(df[['sales_amount', 'quantity', 'price', 'cost']].skew().round(2))

print("\n=== KEY BUSINESS TOTALS ===")
print(f"Total Revenue: {df['sales_amount'].sum():,.0f}")
print(f"Total Orders: {df['order_number'].nunique():,}")
print(f"Total Customers: {df['customer_key'].nunique():,}")
print(f"Avg Order Value: {df.groupby('order_number')['sales_amount'].sum().mean():,.2f}")

# =========== 2. DISTRIBUTION ANALYSIS ===========
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
axes[0].hist(df['sales_amount'], bins=50, color='#2563eb', edgecolor='white')
axes[0].set_title('Distribution of Sales Amount')
axes[1].hist(np.log1p(df['sales_amount']), bins=50, color='#7c3aed', edgecolor='white')
axes[1].set_title('Distribution of Sales Amount (log scale)')
plt.tight_layout()
plt.savefig(f'{CHARTS}/01_sales_amount_distribution.png', bbox_inches='tight')
plt.close()

# =========== 3. Revenue by Category ===========
cat_rev = df.groupby('category')['sales_amount'].sum().sort_values()
fig, ax = plt.subplots(figsize=(8, 4))
ax.barh(cat_rev.index, cat_rev.values, color='#2563eb')
ax.set_title('Total Revenue by Product Category')
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x/1000:,.0f}K'))
plt.tight_layout()
plt.savefig(f'{CHARTS}/02_revenue_by_category.png', bbox_inches='tight')
plt.close()

# =========== 4. Revenue by Country ===========
country_rev = df.groupby('country')['sales_amount'].sum().sort_values()
fig, ax = plt.subplots(figsize=(8, 4))
ax.barh(country_rev.index, country_rev.values, color='#059669')
ax.set_title('Total Revenue by Country')
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x/1000:,.0f}K'))
plt.tight_layout()
plt.savefig(f'{CHARTS}/03_revenue_by_country.png', bbox_inches='tight')
plt.close()

# =========== 5. Monthly Revenue Trend ===========
monthly = df.groupby('order_month')['sales_amount'].sum().sort_index()
fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(monthly.index, monthly.values, marker='o', color='#dc2626', linewidth=2)
ax.set_title('Monthly Revenue Trend')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(f'{CHARTS}/04_monthly_revenue_trend.png', bbox_inches='tight')
plt.close()

# =========== 6. Country x Category heatmap ===========
pivot = df.pivot_table(index='country', columns='category', values='sales_amount', aggfunc='sum', fill_value=0)
fig, ax = plt.subplots(figsize=(7, 5))
im = ax.imshow(pivot.values, cmap='Blues', aspect='auto')
ax.set_xticks(range(len(pivot.columns))); ax.set_xticklabels(pivot.columns, rotation=30, ha='right')
ax.set_yticks(range(len(pivot.index))); ax.set_yticklabels(pivot.index)
ax.set_title('Revenue: Country x Category')
plt.colorbar(im, ax=ax)
plt.tight_layout()
plt.savefig(f'{CHARTS}/05_country_category_heatmap.png', bbox_inches='tight')
plt.close()

# =========== 7. Correlation ===========
corr = df[['sales_amount', 'quantity', 'price', 'cost', 'margin']].corr()
fig, ax = plt.subplots(figsize=(6, 5))
im = ax.imshow(corr.values, cmap='coolwarm', vmin=-1, vmax=1)
ax.set_xticks(range(len(corr.columns))); ax.set_xticklabels(corr.columns, rotation=30, ha='right')
ax.set_yticks(range(len(corr.columns))); ax.set_yticklabels(corr.columns)
ax.set_title('Correlation Matrix')
plt.colorbar(im, ax=ax)
plt.tight_layout()
plt.savefig(f'{CHARTS}/06_correlation_matrix.png', bbox_inches='tight')
plt.close()

# =========== 8. Revenue by Age Group ===========
age_rev = df.dropna(subset=['age_group']).groupby('age_group', observed=True)['sales_amount'].sum()
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(age_rev.index.astype(str), age_rev.values, color='#f59e0b')
ax.set_title('Revenue by Customer Age Group')
plt.tight_layout()
plt.savefig(f'{CHARTS}/07_revenue_by_age_group.png', bbox_inches='tight')
plt.close()

# =========== 9. Top 10 Products ===========
top_prod = df.groupby('product_name')['sales_amount'].sum().sort_values(ascending=False).head(10).sort_values()
fig, ax = plt.subplots(figsize=(9, 5))
ax.barh(top_prod.index, top_prod.values, color='#0891b2')
ax.set_title('Top 10 Products by Revenue')
plt.tight_layout()
plt.savefig(f'{CHARTS}/08_top10_products.png', bbox_inches='tight')
plt.close()

print("\nAll charts saved to charts/ directory.")