-- 1. Create a dedicated schema for analytical models
CREATE SCHEMA IF NOT EXISTS analytics;

-- 2. Create Dimension Table for Outlets
CREATE TABLE IF NOT EXISTS analytics.dim_outlet (
    outlet_id INT PRIMARY KEY,
    outlet_name VARCHAR(100),
    zone_type VARCHAR(50),
    address TEXT
);

-- 3. Create Dimension Table for Menu Items
CREATE TABLE IF NOT EXISTS analytics.dim_item (
    item_id INT PRIMARY KEY,
    item_name VARCHAR(100),
    category VARCHAR(50),
    standard_price NUMERIC(10, 2)
);

-- 4. Create Fact Table for Sales (Filtering out corrupted rows!)
CREATE TABLE IF NOT EXISTS analytics.fact_sales (
    order_id INT PRIMARY KEY,
    outlet_id INT REFERENCES analytics.dim_outlet(outlet_id),
    item_id INT REFERENCES analytics.dim_item(item_id),
    order_date TIMESTAMP,
    quantity INT,
    unit_price NUMERIC(10, 2),
    line_total NUMERIC(10, 2),
    order_status VARCHAR(50)
);