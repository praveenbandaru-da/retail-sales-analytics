/* ============================================================
   SCHEMA.SQL
   Retail Sales Analytics Project
   SQL Server (T-SQL) - Database & Table Structure Only
   ============================================================ */

CREATE DATABASE sales analytics project;
GO
USE sales analytics project;
GO

IF OBJECT_ID('fact_sales', 'U') IS NOT NULL DROP TABLE fact_sales;
IF OBJECT_ID('dim_customers', 'U') IS NOT NULL DROP TABLE dim_customers;
IF OBJECT_ID('dim_products', 'U') IS NOT NULL DROP TABLE dim_products;
GO

CREATE TABLE dim_customers (
    customer_key    INT PRIMARY KEY,
    customer_id     INT,
    customer_number NVARCHAR(10),
    first_name      NVARCHAR(50),
    last_name       NVARCHAR(50),
    country         NVARCHAR(20),
    marital_status  NVARCHAR(10),
    gender          NVARCHAR(10),
    birthdate       DATE NULL,
    create_date     DATE NOT NULL
);
GO

CREATE TABLE dim_products (
    product_key     INT PRIMARY KEY,
    product_id      INT,
    product_number  NVARCHAR(10),
    product_name    NVARCHAR(100),
    category_id     NVARCHAR(10),
    category        NVARCHAR(20),
    subcategory     NVARCHAR(30),
    maintenance     NVARCHAR(3),
    cost            INT,
    product_line    NVARCHAR(20),
    start_date      DATE
);
GO

CREATE TABLE fact_sales (
    order_number    NVARCHAR(10),
    product_key     INT,
    customer_key    INT,
    order_date      DATE,
    shipping_date   DATE,
    due_date        DATE,
    sales_amount    INT,
    quantity        TINYINT,
    price           INT,
    CONSTRAINT FK_fact_product  FOREIGN KEY (product_key)  REFERENCES dim_products(product_key),
    CONSTRAINT FK_fact_customer FOREIGN KEY (customer_key) REFERENCES dim_customers(customer_key)
);
GO

-- Indexes on join/filter columns for query performance
CREATE INDEX idx_fact_sales_product   ON fact_sales(product_key);
CREATE INDEX idx_fact_sales_customer  ON fact_sales(customer_key);
CREATE INDEX idx_fact_sales_orderdate ON fact_sales(order_date);
GO

/* ------------------------------------------------------------
   To load data: right-click SalesAnalytics DB in SSMS
   -> Tasks -> Import Flat File -> select each cleaned CSV
   -> map to the matching table above.
   ------------------------------------------------------------ */