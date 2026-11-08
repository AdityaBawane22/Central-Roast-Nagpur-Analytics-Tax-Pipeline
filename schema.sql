DROP DATABASE IF EXISTS central_roast_nagpur;
CREATE DATABASE central_roast_nagpur;

CREATE DATABASE central_roast_nagpur;

-- Drop existing tables if they exist (clean slate)
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS inventory CASCADE;
DROP TABLE IF EXISTS tax_rules CASCADE;
DROP TABLE IF EXISTS menu_items CASCADE;
DROP TABLE IF EXISTS outlets CASCADE;

-- 1. Outlets Table
CREATE TABLE outlets (
    outlet_id SERIAL PRIMARY KEY,
    outlet_name VARCHAR(100) UNIQUE NOT NULL,
    zone_type VARCHAR(50) NOT NULL,
    address TEXT NOT NULL
);

-- 2. Menu Items Table
CREATE TABLE menu_items (
    item_id SERIAL PRIMARY KEY,
    item_name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50) NOT NULL,
    standard_price DECIMAL(10, 2) NOT NULL
);

-- 3. Tax Rules Table
CREATE TABLE tax_rules (
    tax_rule_id SERIAL PRIMARY KEY,
    category VARCHAR(50) UNIQUE NOT NULL,
    tax_percentage DECIMAL(5, 2) NOT NULL,
    effective_date DATE NOT NULL
);

-- 4. Inventory Table
CREATE TABLE inventory (
    inventory_id SERIAL PRIMARY KEY,
    outlet_id INT REFERENCES outlets(outlet_id) ON DELETE CASCADE,
    item_id INT REFERENCES menu_items(item_id) ON DELETE CASCADE,
    stock_quantity INT NOT NULL,
    reorder_threshold INT NOT NULL,
    CONSTRAINT unique_outlet_item UNIQUE (outlet_id, item_id)
);

-- 5. Orders Table
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    outlet_id INT REFERENCES outlets(outlet_id) ON DELETE CASCADE,
    order_date TIMESTAMP NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    order_status VARCHAR(50) NOT NULL
);

-- 6. Order Items Table
CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(order_id) ON DELETE CASCADE,
    item_id INT REFERENCES menu_items(item_id) ON DELETE CASCADE,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL
);

CREATE TABLE daily_sales_reports (
    report_id SERIAL PRIMARY KEY,
    outlet_id INT REFERENCES outlets(outlet_id) ON DELETE CASCADE,
    report_date DATE NOT NULL,
    total_orders INT NOT NULL,
    gross_revenue DECIMAL(12, 2) NOT NULL,
    total_tax DECIMAL(10, 2) NOT NULL,
    reconciliation_status VARCHAR(50) DEFAULT 'Pending',
    CONSTRAINT unique_outlet_date UNIQUE (outlet_id, report_date)
);

SELECT table_schema, table_name 
FROM information_schema.tables 
WHERE table_schema NOT IN ('pg_catalog', 'information_schema');

SELECT * FROM outlets;

SELECT * FROM menu_items;

SELECT * FROM tax_rules;

SELECT * FROM inventory LIMIT 10;

SELECT * FROM orders ORDER BY order_date DESC LIMIT 10;

SELECT * FROM order_items LIMIT 10;

SELECT * FROM daily_sales_reports ORDER BY report_date DESC LIMIT 10;

TRUNCATE TABLE orders, order_items, daily_sales_reports RESTART IDENTITY CASCADE;

SELECT * FROM orders 
WHERE total_amount < 0 
   OR order_status NOT IN ('Completed', 'Pending') 
   OR order_date > NOW();