import sqlite3
import os
from datetime import datetime
from restaurant_pos.core.path_utils import get_database_path

class DatabaseManager:
    def __init__(self, db_name=None):
        # Use the correct database path relative to executable
        self.db_name = db_name or get_database_path()
        self.init_database()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_database(self):
        """Initialize database with required tables and auto-recovery"""
        print(f"📁 Initializing database at: {self.db_name}")

        conn = None  # Initialize conn variable
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Create categories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create food_items table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS food_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    category TEXT NOT NULL,
                    price REAL NOT NULL,
                    available BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create bills table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bill_number TEXT NOT NULL UNIQUE,
                    customer_name TEXT NOT NULL,
                    customer_mobile TEXT,
                    total_amount REAL NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create bill_items table (for storing individual items in each bill)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bill_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bill_id INTEGER,
                    food_item_id INTEGER,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    total REAL NOT NULL,
                    FOREIGN KEY (bill_id) REFERENCES bills (id),
                    FOREIGN KEY (food_item_id) REFERENCES food_items (id)
                )
            ''')

            conn.commit()
            print("✅ Database initialized successfully")

            # Check if database needs sample data
            self._add_sample_data_if_empty(cursor, conn)

        except sqlite3.Error as e:
            print(f"❌ Database initialization error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def _add_sample_data_if_empty(self, cursor, conn):
        """Insert default food items into the database if food_items table is empty"""
        cursor.execute("SELECT COUNT(*) FROM food_items")
        if cursor.fetchone()[0] > 0:
            return  # Table is not empty, no need to insert sample data

        default_items = [
            # Bread
            ("Naan", "Bread", 25.0),
            ("Roti", "Bread", 8.0),
            ("Butter Naan", "Bread", 35.0),
            ("Garlic Naan", "Bread", 40.0),
            ("Kulcha", "Bread", 30.0),

            # Veg
            ("Paneer Butter Masala", "Main Course (Veg)", 180.0),
            ("Dal Makhani", "Main Course (Veg)", 150.0),
            ("Aloo Gobi", "Main Course (Veg)", 120.0),
            ("Palak Paneer", "Main Course (Veg)", 170.0),
            ("Chole Bhature", "Main Course (Veg)", 140.0),

            # Non-Veg
            ("Butter Chicken", "Main Course (Non-Veg)", 250.0),
            ("Chicken Tikka Masala", "Main Course (Non-Veg)", 230.0),
            ("Mutton Curry", "Main Course (Non-Veg)", 280.0),
            ("Fish Curry", "Main Course (Non-Veg)", 220.0),
            ("Chicken Biryani", "Main Course (Non-Veg)", 200.0),

            # Rice
            ("Jeera Rice", "Rice", 80.0),
            ("Veg Biryani", "Rice", 160.0),
            ("Plain Rice", "Rice", 60.0),
            ("Pulao", "Rice", 120.0),

            # Sweets
            ("Gulab Jamun", "Sweets", 60.0),
            ("Rasmalai", "Sweets", 80.0),
            ("Kheer", "Sweets", 70.0),
            ("Jalebi", "Sweets", 90.0),

            # Cold Drinks
            ("Coca Cola", "Cold Drink", 40.0),
            ("Pepsi", "Cold Drink", 40.0),
            ("Sprite", "Cold Drink", 40.0),
            ("Mango Juice", "Cold Drink", 60.0),
            ("Lassi", "Cold Drink", 50.0),

            # Water
            ("Mineral Water", "Water", 20.0),
            ("Packaged Water", "Water", 15.0),
        ]

        cursor.executemany(
            "INSERT INTO food_items (name, category, price) VALUES (?, ?, ?)",
            default_items
        )

        conn.commit()
        print("✅ Default food items inserted")
