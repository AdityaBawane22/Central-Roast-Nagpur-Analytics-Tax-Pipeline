import duckdb
import pandas as pd
import os

def transform_to_silver():
    db_path = "data_lake/warehouse.duckdb"
    os.makedirs("data_lake", exist_ok=True)
    
    # Connect to DuckDB
    conn = duckdb.connect(db_path)
    
    print("🔄 Running Stage 1: Silver Layer Transformation & Cleaning...")
    
    # 1. Read raw CSVs using Pandas (handles Windows encoding & headers cleanly)
    df_orders = pd.read_csv("data_lake/raw_landing/raw_orders_20261114.csv")
    df_items = pd.read_csv("data_lake/raw_landing/raw_order_items_20261114.csv")
    
    # 2. Clean and standardize data fields in Python
    df_orders["payment_method"] = df_orders["payment_method"].astype(str).str.strip().str.upper()
    df_orders["created_at"] = pd.to_datetime(df_orders["created_at"])
    
    df_items["item_name"] = df_items["item_name"].astype(str).str.strip()
    df_items["created_at"] = pd.to_datetime(df_items["created_at"])
    
    # 3. Register cleaned DataFrames with DuckDB and materialize Silver tables
    conn.register("df_orders_temp", df_orders)
    conn.register("df_items_temp", df_items)
    
    conn.execute("CREATE OR REPLACE TABLE silver_orders AS SELECT * FROM df_orders_temp;")
    conn.execute("CREATE OR REPLACE TABLE silver_order_items AS SELECT * FROM df_items_temp;")
    
    # Verify row counts
    orders_count = conn.execute("SELECT COUNT(*) FROM silver_orders").fetchone()[0]
    items_count = conn.execute("SELECT COUNT(*) FROM silver_order_items").fetchone()[0]
    
    conn.close()
    
    print("--------------------------------------------------")
    print(f"🎉 Stage 1 Complete (Silver Layer):")
    print(f"✔ `silver_orders` table created with {orders_count} rows.")
    print(f"✔ `silver_order_items` table created with {items_count} rows.")
    print(f"💾 Stored locally in DuckDB database -> {db_path}")
    print("--------------------------------------------------")

if __name__ == "__main__":
    transform_to_silver()