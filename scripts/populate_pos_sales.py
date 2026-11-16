import os
import sqlite3
import random
from datetime import datetime

# Define your 6 outlets across Nagpur with their characteristics
OUTLETS = [
    {"id": "OUT-01", "name": "Dharampeth", "zone": "Commercial", "peak_hour": 9},
    {"id": "OUT-02", "name": "IT Park Parsodi", "zone": "Commercial", "peak_hour": 10},
    {"id": "OUT-03", "name": "Civil Lines", "zone": "Commercial", "peak_hour": 11},
    {"id": "OUT-04", "name": "Sadar", "zone": "Commercial", "peak_hour": 16},
    {"id": "OUT-05", "name": "Besa", "zone": "Residential", "peak_hour": 18},
    {"id": "OUT-06", "name": "Manewada", "zone": "Residential", "peak_hour": 19}
]

def populate_sales(target_date="2026-11-14", num_orders_per_store=40):
    storage_dir = "pos_terminal_storage"
    base_date = datetime.strptime(target_date, "%Y-%m-%d")
    
    for outlet in OUTLETS:
        db_filename = f"pos_{outlet['id'].lower()}_{outlet['name'].lower().replace(' ', '_')}.db"
        db_path = os.path.join(storage_dir, db_filename)
        
        if not os.path.exists(db_path):
            print(f"✖ Database not found for {outlet['name']}. Run setup_pos_databases.py first.")
            continue
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Fetch existing menu items from this store's local DB
        cursor.execute("SELECT item_id, item_name, base_price FROM menu_items")
        menu_items = cursor.fetchall()
        
        peak = outlet["peak_hour"]
        orders_inserted = 0
        items_inserted = 0
        
        for i in range(1, num_orders_per_store + 1):
            order_id = f"ORD-{outlet['id']}-{target_date.replace('-', '')}-{i:03d}"
            
            # Simulate transaction time clustered around peak hours
            hour = int(random.gauss(peak, 2))
            hour = max(8, min(22, hour)) # Store hours: 8 AM to 10 PM
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            order_time = base_date.replace(hour=hour, minute=minute, second=second).strftime("%Y-%m-%d %H:%M:%S")
            
            payment_method = random.choices(["UPI", "Cash", "Card"], weights=[65, 25, 10])[0]
            
            # Pick 1 to 3 items for the order
            cart_selection = random.sample(menu_items, k=random.randint(1, 3))
            
            subtotal = 0.0
            line_records = []
            
            for item in cart_selection:
                item_id, item_name, price = item
                qty = random.choices([1, 2, 3], weights=[70, 20, 10])[0]
                
                # Boost beverage/snack sales for commercial zones in the morning
                if outlet["zone"] == "Commercial" and hour < 12:
                    qty += random.choice([0, 1])
                    
                line_total = price * qty
                subtotal += line_total
                
                order_item_id = f"LINE-{order_id}-{item_id}"
                line_records.append((order_item_id, order_id, item_name, price, qty, order_time))
            
            tax_amount = round(subtotal * 0.05, 2) # 5% GST
            grand_total = round(subtotal + tax_amount, 2)
            
            # Insert receipt header into local 'orders' table
            cursor.execute(
                "INSERT OR REPLACE INTO orders VALUES (?, ?, ?, ?, ?, ?)",
                (order_id, payment_method, subtotal, tax_amount, grand_total, order_time)
            )
            orders_inserted += 1
            
            # Insert bill items into local 'order_items' table
            cursor.executemany(
                "INSERT OR REPLACE INTO order_items VALUES (?, ?, ?, ?, ?, ?)",
                line_records
            )
            items_inserted += len(line_records)
            
        conn.commit()
        conn.close()
        print(f"✔ Populated {outlet['name']}: {orders_inserted} orders, {items_inserted} line items recorded locally.")

if __name__ == "__main__":
    populate_sales()