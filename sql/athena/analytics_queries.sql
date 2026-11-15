-- PharmaFlow AWS Athena Analytics
-- Database: pharmaflow_analytics

-- 1. Branches ranked by revenue
SELECT
    branch_id,
    branch_name,
    city,
    transactions,
    units_sold,
    ROUND(revenue, 2) AS revenue
FROM pharmaflow_analytics.branch_revenue
ORDER BY revenue DESC;

-- 2. Top 10 medicines by revenue
SELECT
    medicine_id,
    medicine_name,
    units_sold,
    ROUND(revenue, 2) AS revenue
FROM pharmaflow_analytics.medicine_revenue
ORDER BY revenue DESC
LIMIT 10;

-- 3. Supplier spending
SELECT
    supplier_id,
    supplier_name,
    orders,
    units_ordered,
    ROUND(total_cost, 2) AS total_cost
FROM pharmaflow_analytics.supplier_spend
ORDER BY total_cost DESC;

-- 4. Total branch revenue
SELECT
    ROUND(SUM(revenue), 2) AS total_revenue,
    SUM(transactions) AS total_transactions,
    SUM(units_sold) AS total_units_sold
FROM pharmaflow_analytics.branch_revenue;

-- 5. Total supplier spending
SELECT
    ROUND(SUM(total_cost), 2) AS total_supplier_spend,
    SUM(orders) AS total_orders
FROM pharmaflow_analytics.supplier_spend;
