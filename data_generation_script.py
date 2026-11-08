import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from faker import Faker
import psycopg2
from psycopg2.extras import execute_batch

# Load environment variables from .env file
load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}

if not DB_CONFIG["password"]:
    raise ValueError("CRITICAL: Database password is missing. Check your .env file!")

fake = Faker()

def seed_database():
    conn = psycopg2.connect(**DB_CONFIG)
    print(f"Connected to Database: {DB_CONFIG['dbname']} on Port {DB_CONFIG['port']}")
    cursor = conn.cursor()

    # 1. Seed Outlets
    outlets = [
        ("Central Roast - Dharampeth", "Commercial", "Zenda Chowk, Dharampeth, Nagpur"),
        ("Central Roast - IT Park", "Commercial", "Gayatri Nagar, IT Park, Nagpur"),
        ("Central Roast - Sadar", "Commercial", "Residency Road, Sadar, Nagpur"),
        ("Central Roast - Besa", "Residential", "Besa-Pipla Road, Nagpur"),
        ("Central Roast - Koradi Road", "Residential", "Byramji Town, Koradi Road, Nagpur"),
        ("Central Roast - Wardha Road", "Residential", "Pratap Nagar, Wardha Road, Nagpur"),
    ]
    cursor.executemany(
        "INSERT INTO outlets (outlet_name, zone_type, address) VALUES (%s, %s, %s) ON CONFLICT (outlet_name) DO NOTHING;",
        outlets,
    )

    # 2. Seed Menu Items
    menu_items = [
        ("Oat Milk Latte", "Beverage", 240.00),
        ("Classic Espresso", "Beverage", 150.00),
        ("Cappuccino", "Beverage", 190.00),
        ("Iced Americano", "Beverage", 180.00),
        ("Butter Croissant", "Bakery", 140.00),
        ("Blueberry Muffin", "Bakery", 160.00),
        ("Paneer Tikka Sandwich", "Food", 220.00),
        ("Cold Brew", "Beverage", 210.00),
    ]
    cursor.executemany(
        "INSERT INTO menu_items (item_name, category, standard_price) VALUES (%s, %s, %s) ON CONFLICT (item_name) DO NOTHING;",
        menu_items,
    )

    # 3. Seed Tax Rules
    tax_rules = [
        ("Beverage", 5.00, "2024-01-01"),
        ("Bakery", 5.00, "2024-01-01"),
        ("Food", 5.00, "2024-01-01"),
    ]
    cursor.executemany(
        "INSERT INTO tax_rules (category, tax_percentage, effective_date) VALUES (%s, %s, %s) ON CONFLICT (category) DO NOTHING;",
        tax_rules,
    )
    conn.commit()

    # Retrieve IDs
    cursor.execute("SELECT outlet_id, zone_type FROM outlets;")
    outlet_records = cursor.fetchall()

    cursor.execute("SELECT item_id, standard_price FROM menu_items;")
    item_records = cursor.fetchall()

    # 4. Seed Inventory
    inventory_data = []
    for o_id, _ in outlet_records:
        for i_id, _ in item_records:
            inventory_data.append((o_id, i_id, random.randint(30, 150), 15))
    
    cursor.executemany(
        "INSERT INTO inventory (outlet_id, item_id, stock_quantity, reorder_threshold) VALUES (%s, %s, %s, %s) ON CONFLICT (outlet_id, item_id) DO NOTHING;",
        inventory_data,
    )
    conn.commit()

    print("--- Generating Transactions with Intentional Data Anomalies (Past 30 Days) ---")
    orders_batch = []
    order_items_batch = []
    order_id_counter = 100001
    start_date = datetime.now() - timedelta(days=30)
    
    corrupted_orders_count = 0

    for day in range(30):
        current_day = start_date + timedelta(days=day)

        for outlet_id, zone_type in outlet_records:
            if zone_type == "Commercial":
                daily_order_count = random.randint(40, 70)
                peak_hours = [8, 9, 10, 13, 14, 16]
            else:
                daily_order_count = random.randint(25, 50)
                peak_hours = [11, 16, 17, 18, 19, 20]

            for _ in range(daily_order_count):
                hour = random.choice(peak_hours)
                minute = random.randint(0, 59)
                order_timestamp = current_day.replace(hour=hour, minute=minute, second=0)

                selected_items = random.sample(item_records, k=random.randint(1, 4))
                order_total = 0.0
                order_status = "Completed"

                # --- INTENTIONAL CORRUPTION INJECTION (~3% of orders) ---
                is_corrupted = random.random() < 0.03

                for item_id, price in selected_items:
                    qty = random.randint(1, 3)
                    
                    # Inject negative quantity anomaly on items occasionally
                    if is_corrupted and random.random() < 0.5:
                        qty = -1
                        corrupted_orders_count += 1

                    item_total = float(price) * qty
                    order_total += item_total
                    order_items_batch.append((order_id_counter, item_id, qty, float(price)))

                # Inject order-level anomalies
                if is_corrupted:
                    anomaly_type = random.choice(["negative_total", "weird_status", "future_date"])
                    if anomaly_type == "negative_total":
                        order_total = -abs(order_total)  # Financial mismatch error
                    elif anomaly_type == "weird_status":
                        order_status = "PENDING_UNKNOWN"  # Invalid status string
                    elif anomaly_type == "future_date":
                        order_timestamp = datetime.now() + timedelta(days=365)  # Clock drift error

                orders_batch.append((
                    order_id_counter,
                    outlet_id,
                    order_timestamp,
                    round(order_total, 2),
                    order_status,
                ))
                order_id_counter += 1

    print(f"Inserting {len(orders_batch)} orders (including ~3% injected anomalies)...")
    execute_batch(
        cursor,
        "INSERT INTO orders (order_id, outlet_id, order_date, total_amount, order_status) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (order_id) DO NOTHING;",
        orders_batch,
    )

    print(f"Inserting {len(order_items_batch)} order items...")
    execute_batch(
        cursor,
        "INSERT INTO order_items (order_id, item_id, quantity, unit_price) VALUES (%s, %s, %s, %s);",
        order_items_batch,
    )
    conn.commit()

    # 7. Seed Daily Sales Reports (Staging / Audit Table)
    print("--- Generating Daily Sales Reports Audit Summary ---")
    cursor.execute("""
        SELECT 
            outlet_id, 
            DATE(order_date) as sales_date, 
            COUNT(order_id) as total_orders, 
            SUM(total_amount) as gross_rev
        FROM orders
        WHERE order_date <= NOW()  -- Filter out future date anomalies for clean reporting if needed
        GROUP BY outlet_id, DATE(order_date);
    """)
    daily_summaries = cursor.fetchall()
    
    report_batch = []
    for outlet_id, sales_date, total_orders, gross_rev in daily_summaries:
        gross_rev = float(gross_rev) if gross_rev else 0.0
        total_tax = round(gross_rev * 0.05, 2)
        report_batch.append((
            outlet_id,
            sales_date,
            total_orders,
            gross_rev,
            total_tax,
            "Reconciled"
        ))
        
    execute_batch(
        cursor,
        """
        INSERT INTO daily_sales_reports (outlet_id, report_date, total_orders, gross_revenue, total_tax, reconciliation_status)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (outlet_id, report_date) DO NOTHING;
        """,
        report_batch
    )

    conn.commit()
    cursor.close()
    conn.close()
    print(f"--- Seed Completed! Injected approximately {corrupted_orders_count} corrupted order records into the dataset. ---")

if __name__ == "__main__":
    seed_database()