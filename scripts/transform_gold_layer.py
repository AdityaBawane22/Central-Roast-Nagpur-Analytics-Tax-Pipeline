import duckdb

def transform_to_gold():
    db_path = "data_lake/warehouse.duckdb"
    
    # Connect to DuckDB
    conn = duckdb.connect(db_path)
    
    print("🏆 Running Stage 2: Gold Layer Aggregations & Tax Analytics...")
    
    # 1. Create Gold Table: Outlet Sales and Tax Summary
    conn.execute("""
        CREATE OR REPLACE TABLE gold_outlet_tax_summary AS 
        SELECT 
            source_outlet_id,
            source_outlet_name,
            COUNT(order_id) AS total_orders,
            SUM(subtotal_amount) AS total_revenue_excl_tax,
            SUM(tax_amount) AS total_tax_liability_gst,
            SUM(grand_total) AS total_revenue_incl_tax,
            ROUND(AVG(grand_total), 2) AS average_order_value
        FROM silver_orders
        GROUP BY source_outlet_id, source_outlet_name
        ORDER BY total_revenue_incl_tax DESC;
    """)
    
    # Fetch results to display in terminal
    summary_df = conn.execute("SELECT * FROM gold_outlet_tax_summary").fetchdf()
    
    conn.close()
    
    print("--------------------------------------------------")
    print("🎉 Stage 2 Complete (Gold Layer):")
    print("✔ `gold_outlet_tax_summary` table created successfully.\n")
    print(summary_df.to_string(index=False))
    print("--------------------------------------------------")

if __name__ == "__main__":
    transform_to_gold()