
-- 1. Overall retail sales
SELECT
    COUNT(*) AS transactions,
    SUM(quantity) AS units_sold,
    ROUND(SUM(total_amount), 2) AS revenue
FROM retail_sales;

-- 2. Revenue by pharmacy branch
SELECT
    b.branch_name,
    b.city,
    COUNT(s.sale_id) AS transactions,
    ROUND(SUM(s.total_amount), 2) AS revenue
FROM retail_sales s
JOIN branches b
    ON s.branch_id = b.branch_id
GROUP BY b.branch_id, b.branch_name, b.city
ORDER BY revenue DESC;

-- 3. Top 10 medicines by revenue
SELECT
    m.medicine_name,
    SUM(s.quantity) AS units_sold,
    ROUND(SUM(s.total_amount), 2) AS revenue
FROM retail_sales s
JOIN medicines m
    ON s.medicine_id = m.medicine_id
GROUP BY m.medicine_id, m.medicine_name
ORDER BY revenue DESC
LIMIT 10;

-- 4. Wholesale purchasing by supplier
SELECT
    sp.supplier_name,
    COUNT(w.order_id) AS orders,
    SUM(w.quantity) AS units_ordered,
    ROUND(SUM(w.total_cost), 2) AS total_cost
FROM wholesale_orders w
JOIN suppliers sp
    ON w.supplier_id = sp.supplier_id
GROUP BY sp.supplier_id, sp.supplier_name
ORDER BY total_cost DESC;

-- 5. Monthly retail revenue
SELECT
    DATE_TRUNC('month', sale_date)::date AS month,
    ROUND(SUM(total_amount), 2) AS revenue
FROM retail_sales
GROUP BY 1
ORDER BY 1;
