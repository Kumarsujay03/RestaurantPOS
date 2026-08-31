import sqlite3
from datetime import datetime
from restaurant_pos.core.food_manager import FoodItemManager
from restaurant_pos.core.billing_system import BillingSystem

class RestaurantBillingApp:
    def __init__(self):
        self.food_manager = FoodItemManager()
        self.billing_system = BillingSystem()

    def display_main_menu(self):
        """Display the main menu options"""
        print("\n" + "="*60)
        print("              RESTAURANT BILLING SYSTEM")
        print("="*60)
        print("1. Create New Bill")
        print("2. Search Bill by Number")
        print("3. View Bills by Date")
        print("4. View All Bills")
        print("5. Food Items Management")
        print("6. View Menu")
        print("7. Sales Summary")
        print("8. Exit")
        print("="*60)

    def display_food_menu(self):
        """Display food management menu"""
        print("\n" + "="*50)
        print("           FOOD ITEMS MANAGEMENT")
        print("="*50)
        print("1. Add New Food Item")
        print("2. Update Food Item")
        print("3. Remove Food Item")
        print("4. View All Items")
        print("5. Search Items")
        print("6. View by Category")
        print("7. Back to Main Menu")
        print("="*50)

    def get_valid_input(self, prompt: str, input_type: type = str, min_value=None, max_value=None):
        """Get valid input from user with type checking"""
        while True:
            try:
                user_input = input(prompt)
                if input_type == int:
                    value = int(user_input)
                elif input_type == float:
                    value = float(user_input)
                else:
                    value = user_input.strip()

                if min_value is not None and value < min_value:
                    print(f"Value must be at least {min_value}")
                    continue
                if max_value is not None and value > max_value:
                    print(f"Value must be at most {max_value}")
                    continue

                return value
            except ValueError:
                print(f"Invalid input. Please enter a valid {input_type.__name__}")

    def create_new_bill(self):
        """Create a new bill for a customer"""
        print("\n" + "="*50)
        print("             CREATE NEW BILL")
        print("="*50)

        customer_name = self.get_valid_input("Enter Customer Name: ").strip()
        if not customer_name:
            print("Customer name cannot be empty!")
            return

        customer_mobile = self.get_valid_input("Enter Customer Mobile (optional): ").strip()

        print("\nAvailable Menu Items:")
        self.food_manager.display_menu()

        order_items = []

        while True:
            print(f"\nCurrent Order: {len(order_items)} items")
            print("1. Add Item to Order")
            print("2. Remove Item from Order")
            print("3. View Current Order")
            print("4. Complete Order")
            print("5. Cancel Order")

            choice = self.get_valid_input("Enter choice (1-5): ", int, 1, 5)

            if choice == 1:
                item_id = self.get_valid_input("Enter Item ID: ", int, 1)
                quantity = self.get_valid_input("Enter Quantity: ", int, 1)

                # Check if item exists
                item = self.food_manager.get_item_by_id(item_id)
                if item:
                    order_items.append({'item_id': item_id, 'quantity': quantity})
                    print(f"Added {quantity} x {item['name']} to order")
                else:
                    print("Invalid item ID!")

            elif choice == 2:
                if not order_items:
                    print("No items in order!")
                    continue

                print("\nCurrent Order Items:")
                for i, item in enumerate(order_items, 1):
                    food_item = self.food_manager.get_item_by_id(item['item_id'])
                    print(f"{i}. {food_item['name']} - Quantity: {item['quantity']}")

                item_index = self.get_valid_input("Enter item number to remove: ", int, 1, len(order_items))
                removed_item = order_items.pop(item_index - 1)
                print("Item removed from order")

            elif choice == 3:
                if not order_items:
                    print("No items in order!")
                    continue

                print("\nCurrent Order:")
                total = 0.0
                for item in order_items:
                    food_item = self.food_manager.get_item_by_id(item['item_id'])
                    item_total = food_item['price'] * item['quantity']
                    total += item_total
                    print(f"{food_item['name']} - Qty: {item['quantity']} - Price: ₹{food_item['price']:.2f} - Total: ₹{item_total:.2f}")
                print(f"Order Total: ₹{total:.2f}")

            elif choice == 4:
                if not order_items:
                    print("No items in order!")
                    continue

                bill_number = self.billing_system.create_bill(customer_name, customer_mobile, order_items)
                if bill_number:
                    print(f"\nBill created successfully! Bill Number: {bill_number}")
                else:
                    print("Failed to create bill!")
                break

            elif choice == 5:
                print("Order cancelled!")
                break

    def search_bill(self):
        """Search for a bill by bill number"""
        print("\n" + "="*50)
        print("              SEARCH BILL")
        print("="*50)

        bill_number = self.get_valid_input("Enter Bill Number: ").strip().upper()

        if bill_number:
            self.billing_system.search_bill_by_number(bill_number)
        else:
            print("Bill number cannot be empty!")

    def view_bills_by_date(self):
        """View all bills for a specific date"""
        print("\n" + "="*50)
        print("            VIEW BILLS BY DATE")
        print("="*50)

        date_str = self.get_valid_input("Enter Date (YYYY-MM-DD): ").strip()

        try:
            # Validate date format
            datetime.strptime(date_str, "%Y-%m-%d")
            self.billing_system.display_bills_by_date(date_str)
        except ValueError:
            print("Invalid date format! Please use YYYY-MM-DD")

    def view_all_bills(self):
        """View all bills"""
        print("\n" + "="*50)
        print("              ALL BILLS")
        print("="*50)

        bills = self.billing_system.get_all_bills()

        if not bills:
            print("No bills found!")
            return

        print(f"{'Bill Number':<20} {'Customer':<25} {'Amount':<12} {'Date':<12} {'Time':<10}")
        print("-" * 85)

        for bill in bills:
            print(f"{bill['bill_number']:<20} {bill['customer_name']:<25} ₹{bill['total_amount']:<11.2f} {bill['date']:<12} {bill['time']:<10}")

        print(f"\nTotal Bills: {len(bills)}")

    def add_food_item(self):
        """Add a new food item"""
        print("\n" + "="*50)
        print("            ADD NEW FOOD ITEM")
        print("="*50)

        categories = self.food_manager.get_categories()
        print("Available Categories:")
        for i, category in enumerate(categories, 1):
            print(f"{i}. {category}")
        print(f"{len(categories) + 1}. Add New Category")

        name = self.get_valid_input("Enter Food Item Name: ").strip()
        if not name:
            print("Food item name cannot be empty!")
            return

        category_choice = self.get_valid_input("Select Category (number): ", int, 1, len(categories) + 1)

        if category_choice <= len(categories):
            category = categories[category_choice - 1]
        else:
            category = self.get_valid_input("Enter New Category Name: ").strip()
            if not category:
                print("Category name cannot be empty!")
                return

        price = self.get_valid_input("Enter Price: ₹", float, 0.01)

        if self.food_manager.add_food_item(name, category, price):
            print(f"Food item '{name}' added successfully!")
        else:
            print("Failed to add food item!")

    def update_food_item(self):
        """Update an existing food item"""
        print("\n" + "="*50)
        print("           UPDATE FOOD ITEM")
        print("="*50)

        self.food_manager.display_menu()

        item_id = self.get_valid_input("Enter Item ID to update: ", int, 1)

        item = self.food_manager.get_item_by_id(item_id)
        if not item:
            print("Item not found!")
            return

        print(f"\nCurrent Item: {item['name']} - {item['category']} - ₹{item['price']}")

        print("\nWhat would you like to update?")
        print("1. Name")
        print("2. Category")
        print("3. Price")
        print("4. All")

        choice = self.get_valid_input("Enter choice (1-4): ", int, 1, 4)

        name = category = price = None

        if choice in [1, 4]:
            name = self.get_valid_input(f"Enter new name (current: {item['name']}): ").strip()
            if not name:
                name = None

        if choice in [2, 4]:
            categories = self.food_manager.get_categories()
            print("Available Categories:")
            for i, cat in enumerate(categories, 1):
                print(f"{i}. {cat}")

            cat_choice = self.get_valid_input("Select category (number): ", int, 1, len(categories))
            category = categories[cat_choice - 1]

        if choice in [3, 4]:
            price = self.get_valid_input(f"Enter new price (current: ₹{item['price']}): ₹", float, 0.01)

        if self.food_manager.update_food_item(item_id, name, category, price):
            print("Food item updated successfully!")
        else:
            print("Failed to update food item!")

    def remove_food_item(self):
        """Remove a food item"""
        print("\n" + "="*50)
        print("           REMOVE FOOD ITEM")
        print("="*50)

        self.food_manager.display_menu()

        item_id = self.get_valid_input("Enter Item ID to remove: ", int, 1)

        item = self.food_manager.get_item_by_id(item_id)
        if not item:
            print("Item not found!")
            return

        confirm = self.get_valid_input(f"Are you sure you want to remove '{item['name']}'? (y/n): ").lower()

        if confirm == 'y':
            self.food_manager.remove_food_item(item_id)
        else:
            print("Operation cancelled!")

    def search_food_items(self):
        """Search for food items"""
        print("\n" + "="*50)
        print("            SEARCH FOOD ITEMS")
        print("="*50)

        search_term = self.get_valid_input("Enter search term: ").strip()

        items = self.food_manager.search_items(search_term)

        if not items:
            print("No items found!")
            return

        print(f"\nSearch Results for '{search_term}':")
        print("-" * 60)

        for item in items:
            status = "✓" if item['available'] else "✗"
            print(f"{item['id']:2d}. {item['name']:<30} {item['category']:<20} ₹{item['price']:>6.2f} {status}")

    def view_by_category(self):
        """View items by category"""
        print("\n" + "="*50)
        print("           VIEW BY CATEGORY")
        print("="*50)

        categories = self.food_manager.get_categories()

        if not categories:
            print("No categories found!")
            return

        print("Available Categories:")
        for i, category in enumerate(categories, 1):
            print(f"{i}. {category}")

        choice = self.get_valid_input("Select category (number): ", int, 1, len(categories))
        selected_category = categories[choice - 1]

        items = self.food_manager.get_items_by_category(selected_category)

        if not items:
            print(f"No items found in category: {selected_category}")
            return

        print(f"\nItems in '{selected_category}':")
        print("-" * 60)

        for item in items:
            status = "✓" if item['available'] else "✗"
            print(f"{item['id']:2d}. {item['name']:<30} ₹{item['price']:>6.2f} {status}")

    def view_sales_summary(self):
        """View sales summary"""
        print("\n" + "="*50)
        print("            SALES SUMMARY")
        print("="*50)

        print("1. Overall Summary")
        print("2. Date Range Summary")

        choice = self.get_valid_input("Enter choice (1-2): ", int, 1, 2)

        if choice == 1:
            summary = self.billing_system.get_sales_summary()
        else:
            start_date = self.get_valid_input("Enter Start Date (YYYY-MM-DD): ").strip()
            end_date = self.get_valid_input("Enter End Date (YYYY-MM-DD): ").strip()

            try:
                datetime.strptime(start_date, "%Y-%m-%d")
                datetime.strptime(end_date, "%Y-%m-%d")
                summary = self.billing_system.get_sales_summary(start_date, end_date)
            except ValueError:
                print("Invalid date format! Please use YYYY-MM-DD")
                return

        print("\n" + "="*50)
        print("              SALES REPORT")
        print("="*50)
        print(f"Total Bills: {summary['total_bills']}")
        print(f"Total Sales: ₹{summary['total_sales']:.2f}")
        print(f"Average Bill Amount: ₹{summary['average_bill']:.2f}")
        print("="*50)

    def manage_food_items(self):
        """Food items management submenu"""
        while True:
            self.display_food_menu()

            choice = self.get_valid_input("Enter your choice (1-7): ", int, 1, 7)

            if choice == 1:
                self.add_food_item()
            elif choice == 2:
                self.update_food_item()
            elif choice == 3:
                self.remove_food_item()
            elif choice == 4:
                self.food_manager.display_menu()
            elif choice == 5:
                self.search_food_items()
            elif choice == 6:
                self.view_by_category()
            elif choice == 7:
                break

            input("\nPress Enter to continue...")

    def run(self):
        """Main application loop"""
        print("Welcome to Restaurant Billing System!")
        print("Initializing database...")

        try:
            while True:
                self.display_main_menu()

                choice = self.get_valid_input("Enter your choice (1-8): ", int, 1, 8)

                if choice == 1:
                    self.create_new_bill()
                elif choice == 2:
                    self.search_bill()
                elif choice == 3:
                    self.view_bills_by_date()
                elif choice == 4:
                    self.view_all_bills()
                elif choice == 5:
                    self.manage_food_items()
                elif choice == 6:
                    self.food_manager.display_menu()
                elif choice == 7:
                    self.view_sales_summary()
                elif choice == 8:
                    print("\nThank you for using Restaurant Billing System!")
                    print("Goodbye!")
                    break

                if choice != 5:  # Don't pause after food management (it has its own pause)
                    input("\nPress Enter to continue...")

        except KeyboardInterrupt:
            print("\n\nProgram interrupted by user. Goodbye!")
        except Exception as e:
            print(f"An error occurred: {e}")

def main():
    """Entry point for the command-line billing application."""
    app = RestaurantBillingApp()
    app.run()


if __name__ == "__main__":
    main()
