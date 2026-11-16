import os
import sqlite3
import pandas as pd
from datetime import datetime

# Define your 6 outlets
OUTLETS = [
    {"id": "OUT-01", "name": "Dharampeth"},
    {"id": "OUT-02", "name": "IT Park Parsodi"},
    {"id": "OUT-03", "name": "Civil Lines"},
    {"id": "OUT-04", "name": "Sadar"},
    {"id": "OUT-05", "name": "Besa"},
    {"id": "OUT-06", "name": "Manewada"}
]

def run_ingestion_pipeline(target_date="2026-11-14"):
    storage_dir = "pos_terminal_storage"
    datalake_dir = "data_lake/raw_landing"
    
    # Ensure data lake landing directory exists
    os.makedirs(datalake_dir, exist_ok=True)
    
    all_orders = []
    all_order_items = []
    
    print("🚀 Starting Ingestion Pipeline from Local PoS Storage to Data Lake...")
    
    for outlet in OUTLETS:
        db_filename = f"pos_{outlet['id'].lower()}_{outlet['name'].lower().replace(' ', '_')}.db"
        db_path = os.path.join(storage_dir, db_filename)
        
        if not os.path.exists(db_path):
            print(f"⚠ Warning: Database for {outlet['name']} not found at {db_path}. Skipping.")
            continue
            
        # Connect to the local PoS database (Extraction)
        conn = sqlite3.connect(db_path)
        
        # Read raw tables into Pandas DataFrames
        df_orders = pd.read_sql_query("SELECT * FROM orders", conn)
        df_items = pd.read_sql_query("SELECT * FROM order_items", conn)
        
        conn.close()
        
        # Inject metadata lineage (Tracking which store this data came from)
        df_orders["source_outlet_id"] = outlet["id"]
        df_orders["source_outlet_name"] = outlet["name"]
        
        df_items["source_outlet_id"] = outlet["id"]
        
        all_orders.append(df_orders)
        all_order_items.append(df_items)
        
        print(f"✔ Extracted & Tagged: {outlet['name']} ({len(df_orders)} orders, {len(df_items)} items)")
        
    if all_orders and all_order_items:
        # Combine data from all 6 stores into unified master datasets
        master_orders = pd.concat(all_orders, ignore_index=True)
        master_items = pd.concat(all_order_items, ignore_index=True)
        
        # Land the raw data into the Data Lake (Load step)
        date_str = target_date.replace("-", "")
        orders_output_path = os.path.join(datalake_dir, f"raw_orders_{date_str}.csv")
        items_output_path = os.path.join(datalake_dir, f"raw_order_items_{date_str}.csv")
        
        master_orders.to_csv(orders_output_path, index=False)
        master_items.to_csv(items_output_path, index=False)
        
        print("\n--------------------------------------------------")
        print(f"🎉 Ingestion Complete! Data successfully landed in Data Lake:")
        print(f"📁 Orders Landed At -> {orders_output_path} ({len(master_orders)} total records)")
        print(f"📁 Items Landed At  -> {items_output_path} ({len(master_items)} total records)")
        print("--------------------------------------------------")
    else:
        print("✖ Ingestion failed: No data found across any outlet databases.")

if __name__ == "__main__":
    run_ingestion_pipeline()