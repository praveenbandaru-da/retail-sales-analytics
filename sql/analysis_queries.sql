/* ============================================================
   ANALYSIS_QUERIES.SQL
   Retail Sales Analytics Project
   SQL Server (T-SQL) - Business Analysis Query Bank
   Run schema.sql first and load data before running these.
   ============================================================ */
USE sales analytics project;
GO

-- ============================================================
-- Q1: Basic SELECT / WHERE / ORDER BY
-- Top 10 highest-value single line-item sales
-- ============================================================
SELECT TOP 10 order_number, product_key, customer_key, order_date, sales_amount
FROM fact_sales
WHERE sales_amount > 1000
ORDER BY sales_amount DESC;
GO

-- ============================================================
-- Q2: GROUP BY / HAVING
-- Categories with total revenue above $500,000
-- ============================================================
SELECT p.category,
       SUM(f.sales_amount) AS total_revenue,
       COUNT(*) AS line_items
FROM fact_sales f
JOIN dim_products p ON f.product_key = p.product_key
GROUP BY p.category
HAVING SUM(f.sales_amount) > 500000
ORDER BY total_revenue DESC;
GO

-- ============================================================
-- Q3: CASE statement
-- Customer revenue tiers
-- ============================================================
SELECT
    c.customer_key,
    c.first_name + ' ' + c.last_name AS customer_name,
    SUM(f.sales_amount) AS total_spent,
    CASE
        WHEN SUM(f.sales_amount) >= 5000 THEN 'High Value'
        WHEN SUM(f.sales_amount) >= 1000 THEN 'Mid Value'
        ELSE 'Low Value'
    END AS customer_tier
FROM fact_sales f
JOIN dim_customers c ON f.customer_key = c.customer_key
GROUP BY c.customer_key, c.first_name, c.last_name
ORDER BY total_spent DESC;
GO

-- ============================================================
-- Q4: Multi-table JOIN
-- Revenue by country and category
-- ============================================================
SELECT c.country, p.category, SUM(f.sales_amount) AS revenue
FROM fact_sales f
JOIN dim_customers c ON f.customer_key = c.customer_key
JOIN dim_products p ON f.product_key = p.product_key
WHERE c.country <> 'Unknown'
GROUP BY c.country, p.category
ORDER BY c.country, revenue DESC;
GO

-- ============================================================
-- Q5: LEFT JOIN
-- Products that were never sold
-- ============================================================
SELECT TOP 10 p.product_key, p.product_name, p.category, p.cost
FROM dim_products p
LEFT JOIN fact_sales f ON p.product_key = f.product_key
WHERE f.product_key IS NULL
ORDER BY p.cost DESC;
GO

-- ============================================================
-- Q6: Subquery
-- Customers who spent 10x above the overall average line-item amount
-- ============================================================
SELECT customer_key, total_spent
FROM (
    SELECT customer_key, SUM(sales_amount) AS total_spent
    FROM fact_sales
    GROUP BY customer_key
) AS cust_totals
WHERE total_spent > (SELECT AVG(CAST(sales_amount AS FLOAT)) FROM fact_sales) * 10
ORDER BY total_spent DESC;
GO

-- ============================================================
-- Q7: CTE + LAG() window function
-- Month-over-month revenue change
-- ============================================================
WITH monthly_revenue AS (
    SELECT FORMAT(order_date, 'yyyy-MM') AS sales_month, SUM(sales_amount) AS revenue
    FROM fact_sales
    GROUP BY FORMAT(order_date, 'yyyy-MM')
)
SELECT sales_month, revenue,
       LAG(revenue) OVER (ORDER BY sales_month) AS prev_month_revenue,
       revenue - LAG(revenue) OVER (ORDER BY sales_month) AS mom_change
FROM monthly_revenue
ORDER BY sales_month;
GO

-- ============================================================
-- Q8: RANK() with PARTITION BY
-- Best-selling product per country
-- ============================================================
WITH ranked AS (
    SELECT c.country, p.product_name, SUM(f.sales_amount) AS revenue,
           RANK() OVER (PARTITION BY c.country ORDER BY SUM(f.sales_amount) DESC) AS rnk
    FROM fact_sales f
    JOIN dim_customers c ON f.customer_key = c.customer_key
    JOIN dim_products p ON f.product_key = p.product_key
    WHERE c.country <> 'Unknown'
    GROUP BY c.country, p.product_name
)
SELECT country, product_name, revenue
FROM ranked
WHERE rnk = 1
ORDER BY revenue DESC;
GO

-- ============================================================
-- Q9: Running total with SUM() OVER
-- Cumulative revenue by month
-- ============================================================
WITH monthly AS (
    SELECT FORMAT(order_date, 'yyyy-MM') AS sales_month, SUM(sales_amount) AS revenue
    FROM fact_sales
    GROUP BY FORMAT(order_date, 'yyyy-MM')
)
SELECT sales_month, revenue,
       SUM(revenue) OVER (ORDER BY sales_month) AS cumulative_revenue
FROM monthly
ORDER BY sales_month;
GO

-- ============================================================
-- Q10: CREATE VIEW
-- Reusable customer summary view
-- ============================================================
IF OBJECT_ID('vw_customer_summary', 'V') IS NOT NULL DROP VIEW vw_customer_summary;
GO
CREATE VIEW vw_customer_summary AS
SELECT
    c.customer_key,
    c.first_name + ' ' + c.last_name AS customer_name,
    c.country,
    c.gender,
    COUNT(DISTINCT f.order_number) AS total_orders,
    SUM(f.sales_amount) AS total_spent,
    ROUND(AVG(CAST(f.sales_amount AS FLOAT)), 2) AS avg_line_item_value,
    MIN(f.order_date) AS first_purchase,
    MAX(f.order_date) AS last_purchase
FROM dim_customers c
JOIN fact_sales f ON c.customer_key = f.customer_key
GROUP BY c.customer_key, c.first_name, c.last_name, c.country, c.gender;
GO

SELECT TOP 5 * FROM vw_customer_summary ORDER BY total_spent DESC;
GO

-- ============================================================
-- Index usage verification (SSMS equivalent of EXPLAIN QUERY PLAN)
-- Press Ctrl+L for Estimated Execution Plan, or run below for I/O stats
-- ============================================================
SET STATISTICS IO ON;
SELECT * FROM fact_sales WHERE customer_key = 1133;
SET STATISTICS IO OFF;
GO