import os
import sqlite3

# Define your 6 outlets across Nagpur
OUTLETS = [
    {"id": "OUT-01", "name": "Dharampeth", "zone": "Commercial"},
    {"id": "OUT-02", "name": "IT Park Parsodi", "zone": "Commercial"},
    {"id": "OUT-03", "name": "Civil Lines", "zone": "Commercial"},
    {"id": "OUT-04", "name": "Sadar", "zone": "Commercial"},
    {"id": "OUT-05", "name": "Besa", "zone": "Residential"},
    {"id": "OUT-06", "name": "Manewada", "zone": "Residential"}
]

def initialize_pos_storage():
    storage_dir = "pos_terminal_storage"
    os.makedirs(storage_dir, exist_ok=True)
    
    for outlet in OUTLETS:
        # Each outlet gets its own local database file acting as its PoS machine storage
        db_filename = f"pos_{outlet['id'].lower()}_{outlet['name'].lower().replace(' ', '_')}.db"
        db_path = os.path.join(storage_dir, db_filename)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Taxes Master Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS taxes (
            tax_id TEXT PRIMARY KEY,
            tax_name TEXT,
            tax_rate_pct REAL
        )
        """)
        
        # 2. Menu Items Table (Linked to Taxes)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            item_id TEXT PRIMARY KEY,
            item_name TEXT,
            category TEXT,
            base_price REAL,
            tax_id TEXT,
            FOREIGN KEY(tax_id) REFERENCES taxes(tax_id)
        )
        """)
        
        # 3. Orders (Receipt Header) Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            payment_method TEXT,
            subtotal_amount REAL,
            tax_amount REAL,
            grand_total REAL,
            created_at TEXT
        )
        """)
        
        # 4. Order Items (Bill Line Items) Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id TEXT PRIMARY KEY,
            order_id TEXT,
            item_name TEXT,
            unit_price REAL,
            quantity INTEGER,
            created_at TEXT,
            FOREIGN KEY(order_id) REFERENCES orders(order_id)
        )
        """)
        
        # Insert baseline tax and shared menu data
        cursor.execute("INSERT OR IGNORE INTO taxes VALUES ('TAX-01', 'Standard GST', 5.0)")
        
        menu_data = [
            ('ITM-01', 'Oat Milk Latte', 'Beverages', 240.0, 'TAX-01'),
            ('ITM-02', 'Butter Croissant', 'Snacks', 160.0, 'TAX-01'),
            ('ITM-03', 'Cold Brew Coffee', 'Drinks', 210.0, 'TAX-01'),
            ('ITM-04', 'Chocolate Brownie', 'Snacks', 150.0, 'TAX-01'),
            ('ITM-05', 'Paneer Tikka Panini', 'Food', 280.0, 'TAX-01'),
            ('ITM-06', 'Belgian Frappe', 'Drinks', 250.0, 'TAX-01')
        ]
        cursor.executemany("INSERT OR IGNORE INTO menu_items VALUES (?, ?, ?, ?, ?)", menu_data)
        
        conn.commit()
        conn.close()
        print(f"✔ PoS Storage Initialized: {outlet['name']} ({outlet['zone']}) -> {db_path}")

if __name__ == "__main__":
    initialize_pos_storage()