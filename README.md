# Retail Sales Analytics — End-to-End Data Analysis Project

An end-to-end data analytics project on a retail sales dataset (18,484 customers, 295 products, 60,398 transactions), covering data cleaning, SQL analysis, exploratory data analysis, statistical testing, and interactive dashboards in both **Tableau** and **Power BI**.

## Business Problem

The business had no consolidated view connecting customer demographics, product performance, and sales trends — making it difficult to allocate marketing spend, plan inventory, or prioritize growth initiatives with confidence. This project builds that view from raw data to an executive-ready dashboard and report.

## Key Results

| Metric | Value |
|---|---|
| Total Revenue | $29,356,250 |
| Total Orders | 27,659 |
| Average Order Value | $1,061.36 |
| Repeat Purchase Rate | 37.1% |
| Revenue from Bikes | 96.5% |

**Top findings:**
- Revenue is heavily concentrated in two markets (US + Australia = 62%) and two product lines (Mountain-200, Road-150 = 44%+)
- Category mix (Bikes vs. Accessories vs. Clothing) is consistent across every country — a single global cross-sell initiative would apply everywhere, no market-specific strategy needed
- Statistical testing (Phase 8) revealed that customer age has **no meaningful individual-level correlation with spend** (r = -0.037) — a bar chart showing older age groups with higher total revenue was driven by group size, not individual behavior. This overturned an initial recommendation to shift marketing budget toward older demographics.

Full findings and business recommendations: [`reports/executive_summary.docx`](reports/executive_summary.docx)

## Repo Structure

```
├── data/
│   ├── raw/                    # Original source files
│   └── cleaned/                # Cleaned tables + merged flat table
├── sql/
│   ├── schema.sql              # Database & table creation (SQL Server / T-SQL)
│   └── analysis_queries.sql    # 10-query analysis bank: joins, CTEs, window functions, views
├── python/
│   ├── 01_cleaning.py          # Data cleaning with documented, evidence-based fixes
│   ├── merge_files.py          # Builds the merged flat table from the 3 cleaned tables
│   ├── 02_eda.py               # Exploratory analysis: distributions, trends, segments
│   └── 03_stats.py             # Hypothesis testing, confidence intervals, ANOVA, chi-square
├── dashboard/                  #  Power BI (.pbix) dashboard files
└── reports/
    ├── executive_summary.docx  # Leadership-facing summary report
    └── *.png                   # EDA chart outputs (distributions, trends, segments, correlations)
```

## Data Model

Star schema with two dimension tables and one fact table:

```
dim_customers (18,484)         dim_products (295)
     customer_key  ─┐              ┌─  product_key
                     │              │
                  fact_sales (60,398)
         order_number, order_date, sales_amount,
              quantity, price
```

## Methodology

1. **Data Cleaning** — resolved missing categorical values (product categories, country, gender), corrected a product cost data-entry error, and imputed 19 missing order dates using a verified deterministic 7-day order-to-shipping rule. Zero rows were dropped; missing values were labeled or derived, never guessed.
2. **SQL Analysis** — built a normalized SQL Server schema with primary/foreign keys and indexes; wrote a 10-query bank progressing from basic filtering through CTEs, window functions (`RANK`, `LAG`, running totals), and a reusable view.
3. **Exploratory Data Analysis** — distribution, correlation, trend, and segment analysis in Python (Pandas/Matplotlib).
4. **Statistical Analysis** — validated EDA findings with hypothesis tests (t-test, ANOVA, chi-square) and confidence intervals rather than relying on visual impressions alone.
5. **Dashboard Design** — built interactive dashboards in both Tableau and Power BI with KPI cards, trend charts, geographic maps, and cross-filtering.
6. **Executive Reporting** — synthesized findings into prioritized, evidence-backed business recommendations.

## Tools Used

`Python (Pandas, NumPy, Matplotlib, SciPy)` · `SQL Server / T-SQL` · `Tableau` · `Power BI` · `Excel`

## Author

Praveen — B.Tech Information Technology, Guru Ghasidas University
