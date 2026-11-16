import sqlite3
import os

def view_data():
    db_path = "pos_terminal_storage/pos_out-01_dharampeth.db" # Checking Dharampeth store
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("--- RECENT ORDERS (DHARAMPETH STORE) ---")
    cursor.execute("SELECT order_id, payment_method, grand_total, created_at FROM orders LIMIT 5;")
    for row in cursor.fetchall():
        print(row)
        
    print("\n--- ORDER LINE ITEMS ---")
    cursor.execute("SELECT order_item_id, item_name, unit_price, quantity FROM order_items LIMIT 5;")
    for row in cursor.fetchall():
        print(row)
        
    conn.close()

if __name__ == "__main__":
    view_data()