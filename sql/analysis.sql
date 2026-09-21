-- ============================================================
-- End-to-End Retail BI Project (Real Data)
-- Dataset: Sample Superstore (9,994 real transactions, 2014-2017)
-- Run against retail_real.db (SQLite)
-- ============================================================

-- 1. JOIN + GROUP BY: Revenue and profit by region
SELECT
    o.region,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(oi.sales), 2)  AS total_revenue,
    ROUND(SUM(oi.profit), 2) AS total_profit
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY o.region
ORDER BY total_revenue DESC;


-- 2. JOIN + GROUP BY: Revenue and margin by product category
SELECT
    p.category,
    ROUND(SUM(oi.sales), 2)  AS revenue,
    ROUND(SUM(oi.profit), 2) AS profit,
    ROUND(100.0 * SUM(oi.profit) / SUM(oi.sales), 1) AS profit_margin_pct
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY profit DESC;


-- 3. CTE: Customer lifetime value and tiering
WITH customer_totals AS (
    SELECT
        o.customer_id,
        COUNT(DISTINCT o.order_id) AS num_orders,
        ROUND(SUM(oi.sales), 2)    AS lifetime_value
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY o.customer_id
)
SELECT
    ct.customer_id,
    c.customer_name,
    ct.num_orders,
    ct.lifetime_value,
    CASE
        WHEN ct.lifetime_value >= 5000 THEN 'High value'
        WHEN ct.lifetime_value >= 2000 THEN 'Mid value'
        ELSE 'Low value'
    END AS customer_tier
FROM customer_totals ct
JOIN customers c ON ct.customer_id = c.customer_id
ORDER BY ct.lifetime_value DESC
LIMIT 20;


-- 4. Window function: Month-over-month revenue with running total
WITH monthly_revenue AS (
    SELECT
        strftime('%Y-%m', o.order_date) AS month,
        ROUND(SUM(oi.sales), 2) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY month
)
SELECT
    month,
    revenue,
    ROUND(revenue - LAG(revenue) OVER (ORDER BY month), 2) AS mom_change,
    ROUND(SUM(revenue) OVER (ORDER BY month), 2)           AS running_total
FROM monthly_revenue
ORDER BY month;


-- 5. Window function: Rank sub-categories by profit within each category
WITH subcat_profit AS (
    SELECT
        p.category,
        p.sub_category,
        ROUND(SUM(oi.profit), 2) AS profit
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY p.category, p.sub_category
)
SELECT
    category,
    sub_category,
    profit,
    RANK() OVER (PARTITION BY category ORDER BY profit DESC) AS rank_in_category
FROM subcat_profit
ORDER BY category, rank_in_category;


-- 6. Discount impact: average discount vs average margin by category
SELECT
    p.category,
    ROUND(AVG(oi.discount), 3)                       AS avg_discount,
    ROUND(100.0 * SUM(oi.profit) / SUM(oi.sales), 1)  AS profit_margin_pct
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY avg_discount DESC;


-- 7. Subquery: Customers whose total spend is above the average customer spend
SELECT
    c.customer_id,
    c.customer_name,
    c.segment,
    ROUND(SUM(oi.sales), 2) AS total_spend
FROM customers c
JOIN orders o        ON c.customer_id = o.customer_id
JOIN order_items oi  ON o.order_id = oi.order_id
GROUP BY c.customer_id
HAVING total_spend > (
    SELECT AVG(cust_total)
    FROM (
        SELECT SUM(oi2.sales) AS cust_total
        FROM orders o2
        JOIN order_items oi2 ON o2.order_id = oi2.order_id
        GROUP BY o2.customer_id
    )
)
ORDER BY total_spend DESC
LIMIT 20;


-- 8. Sub-categories that are unprofitable overall (a real, useful finding)
SELECT
    p.sub_category,
    ROUND(SUM(oi.sales), 2)  AS revenue,
    ROUND(SUM(oi.profit), 2) AS profit
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.sub_category
HAVING profit < 0
ORDER BY profit ASC;
