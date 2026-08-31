import sqlite3

from restaurant_pos.core.database import DatabaseManager
from typing import List, Dict, Optional

class FoodItemManager:
    def __init__(self):
        self.db = DatabaseManager()

    def add_food_item(self, name: str, category: str, price: float, available: bool = True) -> bool:
        """Add a new food item to the menu"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO food_items (name, category, price, available) VALUES (?, ?, ?, ?)",
                (name, category, price, available)
            )

            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            print(f"Error: Food item '{name}' already exists!")
            return False
        except Exception as e:
            print(f"Error adding food item: {e}")
            return False

    def update_food_item(self, item_id: int, name: str = None, category: str = None, price: float = None, available: bool = None) -> bool:
        """Update an existing food item"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Build dynamic update query
            updates = []
            params = []

            if name:
                updates.append("name = ?")
                params.append(name)
            if category:
                updates.append("category = ?")
                params.append(category)
            if price is not None:
                updates.append("price = ?")
                params.append(price)
            if available is not None:
                updates.append("available = ?")
                params.append(available)

            if not updates:
                print("No updates provided!")
                return False

            params.append(item_id)
            query = f"UPDATE food_items SET {', '.join(updates)} WHERE id = ?"

            cursor.execute(query, params)

            if cursor.rowcount == 0:
                print(f"No food item found with ID: {item_id}")
                return False

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating food item: {e}")
            return False

    def remove_food_item(self, item_id: int) -> bool:
        """Remove a food item from the menu"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Check if item exists
            cursor.execute("SELECT name FROM food_items WHERE id = ?", (item_id,))
            item = cursor.fetchone()

            if not item:
                print(f"No food item found with ID: {item_id}")
                return False

            # Remove the item
            cursor.execute("DELETE FROM food_items WHERE id = ?", (item_id,))

            conn.commit()
            conn.close()
            print(f"Food item '{item[0]}' removed successfully!")
            return True
        except Exception as e:
            print(f"Error removing food item: {e}")
            return False

    def get_all_items(self) -> List[Dict]:
        """Get all food items from the menu"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id, name, category, price, available FROM food_items ORDER BY category, name"
            )

            items = []
            for row in cursor.fetchall():
                items.append({
                    'id': row[0],
                    'name': row[1],
                    'category': row[2],
                    'price': row[3],
                    'available': row[4]
                })

            conn.close()
            return items
        except Exception as e:
            print(f"Error fetching food items: {e}")
            return []

    def get_items_by_category(self, category: str) -> List[Dict]:
        """Get all items in a specific category"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id, name, category, price, available FROM food_items WHERE category = ? ORDER BY name",
                (category,)
            )

            items = []
            for row in cursor.fetchall():
                items.append({
                    'id': row[0],
                    'name': row[1],
                    'category': row[2],
                    'price': row[3],
                    'available': row[4]
                })

            conn.close()
            return items
        except Exception as e:
            print(f"Error fetching items by category: {e}")
            return []

    def add_category(self, category_name: str) -> bool:
        """Add a new category to the categories table"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Insert into categories table
            cursor.execute(
                "INSERT INTO categories (name) VALUES (?)",
                (category_name,)
            )

            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            print(f"Category '{category_name}' already exists!")
            return False
        except Exception as e:
            print(f"Error adding category: {e}")
            return False

    def get_categories(self) -> List[str]:
        """Get all unique categories from both categories table and food_items"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Get categories from the categories table
            cursor.execute("SELECT name FROM categories ORDER BY name")
            categories_from_table = [row[0] for row in cursor.fetchall()]

            # Get categories from food_items
            cursor.execute("SELECT DISTINCT category FROM food_items ORDER BY category")
            categories_from_items = [row[0] for row in cursor.fetchall()]

            # Combine and deduplicate
            all_categories = list(set(categories_from_table + categories_from_items))
            all_categories.sort()

            conn.close()
            return all_categories
        except Exception as e:
            print(f"Error fetching categories: {e}")
            return []

    def search_items(self, search_term: str) -> List[Dict]:
        """Search for food items by name"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id, name, category, price, available FROM food_items WHERE name LIKE ? ORDER BY name",
                (f"%{search_term}%",)
            )

            items = []
            for row in cursor.fetchall():
                items.append({
                    'id': row[0],
                    'name': row[1],
                    'category': row[2],
                    'price': row[3],
                    'available': row[4]
                })

            conn.close()
            return items
        except Exception as e:
            print(f"Error searching items: {e}")
            return []

    def get_item_by_id(self, item_id: int) -> Optional[Dict]:
        """Get a specific food item by ID"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id, name, category, price, available FROM food_items WHERE id = ?",
                (item_id,)
            )

            row = cursor.fetchone()
            if row:
                item = {
                    'id': row[0],
                    'name': row[1],
                    'category': row[2],
                    'price': row[3],
                    'available': row[4]
                }
                conn.close()
                return item

            conn.close()
            return None
        except Exception as e:
            print(f"Error fetching item by ID: {e}")
            return None

    def display_menu(self):
        """Display the complete menu organized by categories"""
        categories = self.get_categories()

        if not categories:
            print("No items in the menu!")
            return

        print("\n" + "="*60)
        print("                    RESTAURANT MENU")
        print("="*60)

        for category in categories:
            items = self.get_items_by_category(category)
            if items:
                print(f"\n{category.upper()}")
                print("-" * len(category))

                for item in items:
                    status = "✓" if item['available'] else "✗"
                    print(f"{item['id']:2d}. {item['name']:<30} ₹{item['price']:>6.2f} {status}")

        print("\n" + "="*60)
        print("✓ = Available, ✗ = Not Available")
        print("="*60)

    def update_category(self, old_category: str, new_category: str) -> bool:
        """Update all items in a category to a new category name"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Update all items in the old category to new category
            cursor.execute(
                "UPDATE food_items SET category = ? WHERE category = ?",
                (new_category, old_category)
            )
            items_updated = cursor.rowcount

            # Update or add the new category in categories table
            cursor.execute(
                "INSERT OR IGNORE INTO categories (name) VALUES (?)",
                (new_category,)
            )

            # Remove old category from categories table if it exists
            cursor.execute("DELETE FROM categories WHERE name = ?", (old_category,))

            conn.commit()
            conn.close()

            if items_updated > 0:
                return True
            else:
                print(f"No items found in category: {old_category}")
                return False
        except Exception as e:
            print(f"Error updating category: {e}")
            return False

    def remove_category(self, category_name: str) -> bool:
        """Remove a category and all its items"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Check if category has items
            cursor.execute("SELECT COUNT(*) FROM food_items WHERE category = ?", (category_name,))
            item_count = cursor.fetchone()[0]

            # Remove all items in the category if any exist
            if item_count > 0:
                cursor.execute("DELETE FROM food_items WHERE category = ?", (category_name,))

            # Remove category from categories table
            cursor.execute("DELETE FROM categories WHERE name = ?", (category_name,))
            category_removed = cursor.rowcount > 0

            conn.commit()
            conn.close()

            if item_count > 0 or category_removed:
                print(f"Category '{category_name}' and {item_count} items removed successfully!")
                return True
            else:
                print(f"Category '{category_name}' not found")
                return False
        except Exception as e:
            print(f"Error removing category: {e}")
            return False

    def get_category_item_count(self, category_name: str) -> int:
        """Get the number of items in a category"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM food_items WHERE category = ?", (category_name,))
            count = cursor.fetchone()[0]

            conn.close()
            return count
        except Exception as e:
            print(f"Error getting category item count: {e}")
            return 0

    def category_exists(self, category_name: str) -> bool:
        """Check if a category exists"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM food_items WHERE category = ?", (category_name,))
            count = cursor.fetchone()[0]

            conn.close()
            return count > 0
        except Exception as e:
            print(f"Error checking category existence: {e}")
            return False

    def get_category_statistics(self) -> Dict[str, Dict[str, int]]:
        """Get statistics for all categories"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Get all categories and their item counts
            cursor.execute("""
                SELECT category, 
                       COUNT(*) as total_items,
                       SUM(CASE WHEN available = 1 THEN 1 ELSE 0 END) as available_items,
                       SUM(CASE WHEN available = 0 THEN 1 ELSE 0 END) as unavailable_items
                FROM food_items 
                GROUP BY category 
                ORDER BY category
            """)

            stats = {}
            for row in cursor.fetchall():
                category = row[0]
                stats[category] = {
                    'total_items': row[1],
                    'available_items': row[2],
                    'unavailable_items': row[3]
                }

            conn.close()
            return stats
        except Exception as e:
            print(f"Error getting category statistics: {e}")
            return {}
