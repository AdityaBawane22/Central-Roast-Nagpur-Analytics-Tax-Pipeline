-- 1. Populate dim_outlet from source outlets
INSERT INTO analytics.dim_outlet (outlet_id, outlet_name, zone_type, address)
SELECT outlet_id, outlet_name, zone_type, address
FROM outlets
ON CONFLICT (outlet_id) DO UPDATE 
SET outlet_name = EXCLUDED.outlet_name, 
    zone_type = EXCLUDED.zone_type, 
    address = EXCLUDED.address;

-- 2. Populate dim_item from source menu_items
INSERT INTO analytics.dim_item (item_id, item_name, category, standard_price)
SELECT item_id, item_name, category, standard_price
FROM menu_items
ON CONFLICT (item_id) DO UPDATE 
SET item_name = EXCLUDED.item_name, 
    category = EXCLUDED.category, 
    standard_price = EXCLUDED.standard_price;

-- 3. Populate fact_sales (CLEANED & FILTERED)
-- This joins orders with order_items and excludes corrupted orders/items
INSERT INTO analytics.fact_sales (order_id, outlet_id, item_id, order_date, quantity, unit_price, line_total, order_status)
SELECT 
    o.order_id,
    o.outlet_id,
    oi.item_id,
    o.order_date,
    oi.quantity,
    oi.unit_price,
    (oi.quantity * oi.unit_price) AS line_total,
    o.order_status
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.total_amount >= 0                  -- Filter out negative order totals
  AND o.order_status IN ('Completed', 'Pending') -- Filter out weird statuses
  AND o.order_date <= NOW()                -- Filter out future date anomalies
  AND oi.quantity > 0                      -- Filter out negative quantities
ON CONFLICT (order_id) DO NOTHING;