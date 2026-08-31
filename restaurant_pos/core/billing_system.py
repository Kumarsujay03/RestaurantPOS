from restaurant_pos.core.database import DatabaseManager
from restaurant_pos.core.food_manager import FoodItemManager
from restaurant_pos.core.config import get_bill_header, get_bill_footer, get_currency_symbol, get_bill_prefix
from datetime import datetime
import sqlite3
from typing import List, Dict, Optional
from restaurant_pos.core.printer_utils import EnhancedBillPrinter
from restaurant_pos.core.path_utils import get_bills_directory, get_bill_file_path, ensure_app_directories

class BillingSystem:
    def __init__(self):
        # Ensure all application directories exist
        ensure_app_directories()

        self.db = DatabaseManager()
        self.food_manager = FoodItemManager()
        self.printer = EnhancedBillPrinter()

    def generate_bill_number(self) -> str:
        """Generate a unique bill number"""
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        time_str = now.strftime("%H%M%S")
        prefix = get_bill_prefix()
        return f"{prefix}{date_str}{time_str}"

    def create_bill(self, customer_name: str, customer_mobile: str, order_items: List[Dict], auto_print: bool = True, payment_method: str = 'Cash') -> Optional[str]:
        """
        Create a new bill with payment method tracking
        order_items: List of dictionaries with 'item_id' and 'quantity'
        payment_method: Payment method used (Cash, UPI, Card, etc.)
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Add payment_method column if it doesn't exist (for database upgrade)
            try:
                cursor.execute("ALTER TABLE bills ADD COLUMN payment_method TEXT DEFAULT 'Cash'")
                conn.commit()
                print("✅ Added payment_method column to bills table")
            except sqlite3.OperationalError:
                # Column already exists
                pass

            # Generate bill number
            bill_number = self.generate_bill_number()

            # Calculate total amount and prepare bill items
            total_amount = 0.0
            bill_items = []

            for order_item in order_items:
                item_id = order_item['item_id']
                quantity = order_item['quantity']

                # Get item details
                food_item = self.food_manager.get_item_by_id(item_id)
                if not food_item:
                    print(f"Error: Food item with ID {item_id} not found!")
                    return None

                if not food_item['available']:
                    print(f"Error: {food_item['name']} is not available!")
                    return None

                item_total = food_item['price'] * quantity
                total_amount += item_total

                bill_items.append({
                    'food_item_id': item_id,
                    'name': food_item['name'],
                    'price': food_item['price'],
                    'quantity': quantity,
                    'total': item_total
                })

            if not bill_items:
                print("No valid items in the order!")
                return None

            # Insert bill with payment method
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S")

            cursor.execute(
                "INSERT INTO bills (bill_number, customer_name, customer_mobile, total_amount, date, time, payment_method) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (bill_number, customer_name, customer_mobile, total_amount, date_str, time_str, payment_method)
            )

            bill_id = cursor.lastrowid

            # Insert bill items
            for item in bill_items:
                cursor.execute(
                    "INSERT INTO bill_items (bill_id, food_item_id, quantity, price, total) VALUES (?, ?, ?, ?, ?)",
                    (bill_id, item['food_item_id'], item['quantity'], item['price'], item['total'])
                )

            conn.commit()
            conn.close()

            # Print the bill to terminal
            self.print_bill(bill_number, customer_name, customer_mobile, bill_items, total_amount, date_str, time_str)

            # Print or save the bill if auto_print is enabled
            if auto_print:
                print_result = self.printer.print_or_save_bill(
                    bill_number, customer_name, customer_mobile, bill_items, total_amount, date_str, time_str
                )
                print(f"Print result: {print_result[2]}")

            return bill_number

        except Exception as e:
            print(f"Error creating bill: {e}")
            return None

    def print_bill(self, bill_number: str, customer_name: str, customer_mobile: str, bill_items: List[Dict],
                   total_amount: float, date: str, time: str):
        """Print formatted bill with restaurant details - professional console output"""
        print("\n" + "="*70)
        # Restaurant header
        header = get_bill_header()
        for line in header.split('\n'):
            print(f"{line:^70}")
        print("="*70)

        # Bill details
        print(f"Bill Number: {bill_number}")
        print(f"Customer: {customer_name}")
        if customer_mobile:
            print(f"Mobile: {customer_mobile}")
        print(f"Date: {date}                    Time: {time}")
        print("-"*70)
        print(f"{'Item':<35} {'Qty':<5} {'Price':<12} {'Total':<12}")
        print("-"*70)

        # Items - using Rs instead of rupee symbol for consistency
        for item in bill_items:
            print(f"{item['name']:<35} {item['quantity']:<5} Rs {item['price']:<9.2f} Rs {item['total']:<9.2f}")

        print("-"*70)
        print(f"{'TOTAL AMOUNT':<53} Rs {total_amount:>12.2f}")
        print("="*70)

        # Footer
        footer = get_bill_footer()
        for line in footer.split('\n'):
            print(f"{line:^70}")
        print("="*70)

    def search_bill_by_number(self, bill_number: str) -> Optional[Dict]:
        """Search for a bill by bill number"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Get bill details
            cursor.execute(
                "SELECT id, bill_number, customer_name, customer_mobile, total_amount, date, time, payment_method FROM bills WHERE bill_number = ?",
                (bill_number,)
            )

            bill_row = cursor.fetchone()
            if not bill_row:
                print(f"No bill found with number: {bill_number}")
                return None

            bill_id, bill_number, customer_name, customer_mobile, total_amount, date, time, payment_method = bill_row

            # Get bill items
            cursor.execute("""
                SELECT bi.quantity, bi.price, bi.total, fi.name
                FROM bill_items bi
                JOIN food_items fi ON bi.food_item_id = fi.id
                WHERE bi.bill_id = ?
            """, (bill_id,))

            bill_items = []
            for row in cursor.fetchall():
                bill_items.append({
                    'quantity': row[0],
                    'price': row[1],
                    'total': row[2],
                    'name': row[3]
                })

            conn.close()

            bill_data = {
                'bill_number': bill_number,
                'customer_name': customer_name,
                'customer_mobile': customer_mobile,
                'total_amount': total_amount,
                'date': date,
                'time': time,
                'payment_method': payment_method or 'Cash',
                'items': bill_items
            }

            # Display the bill
            self.print_bill(bill_number, customer_name, customer_mobile, bill_items, total_amount, date, time)

            return bill_data

        except Exception as e:
            print(f"Error searching bill: {e}")
            return None

    def get_bills_by_date(self, date: str) -> List[Dict]:
        """Get all bills for a specific date (format: YYYY-MM-DD)"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT bill_number, customer_name, total_amount, time, payment_method FROM bills WHERE date = ? ORDER BY time",
                (date,)
            )

            bills = []
            for row in cursor.fetchall():
                bills.append({
                    'bill_number': row[0],
                    'customer_name': row[1],
                    'total_amount': row[2],
                    'time': row[3],
                    'payment_method': row[4] or 'Cash'  # Default to Cash if None
                })

            conn.close()
            return bills

        except Exception as e:
            print(f"Error fetching bills by date: {e}")
            return []

    def display_bills_by_date(self, date: str):
        """Display all bills for a specific date"""
        bills = self.get_bills_by_date(date)

        if not bills:
            print(f"No bills found for date: {date}")
            return

        print(f"\n{'='*80}")
        print(f"                    BILLS FOR {date}")
        print(f"{'='*80}")
        print(f"{'Bill Number':<20} {'Customer Name':<25} {'Amount':<15} {'Time':<10}")
        print(f"{'-'*80}")

        total_sales = 0.0
        for bill in bills:
            print(f"{bill['bill_number']:<20} {bill['customer_name']:<25} ₹{bill['total_amount']:<14.2f} {bill['time']:<10}")
            total_sales += bill['total_amount']

        print(f"{'-'*80}")
        print(f"{'TOTAL SALES':<60} ₹{total_sales:>15.2f}")
        print(f"{'TOTAL BILLS':<60} {len(bills):>15}")
        print(f"{'='*80}")

    def get_all_bills(self) -> List[Dict]:
        """Get all bills"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT bill_number, customer_name, total_amount, date, time, payment_method FROM bills ORDER BY date DESC, time DESC"
            )

            bills = []
            for row in cursor.fetchall():
                bills.append({
                    'bill_number': row[0],
                    'customer_name': row[1],
                    'total_amount': row[2],
                    'date': row[3],
                    'time': row[4],
                    'payment_method': row[5] or 'Cash'  # Default to Cash if None
                })

            conn.close()
            return bills

        except Exception as e:
            print(f"Error fetching all bills: {e}")
            return []

    def get_sales_summary(self, start_date: str = None, end_date: str = None) -> Dict:
        """Get sales summary for a date range"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            if start_date and end_date:
                cursor.execute(
                    "SELECT COUNT(*), SUM(total_amount) FROM bills WHERE date BETWEEN ? AND ?",
                    (start_date, end_date)
                )
            else:
                cursor.execute("SELECT COUNT(*), SUM(total_amount) FROM bills")

            result = cursor.fetchone()
            total_bills = result[0] if result[0] else 0
            total_sales = result[1] if result[1] else 0.0

            conn.close()

            return {
                'total_bills': total_bills,
                'total_sales': total_sales,
                'average_bill': total_sales / total_bills if total_bills > 0 else 0
            }

        except Exception as e:
            print(f"Error fetching sales summary: {e}")
            return {'total_bills': 0, 'total_sales': 0.0, 'average_bill': 0.0}

    def enhanced_print_bill(self, bill_number: str) -> tuple:
        """
        Enhanced bill printing using the reliable notepad method
        Returns: (success: bool, file_path: str, message: str)
        """
        try:
            # Get bill details
            bill_data = self.search_bill_by_number(bill_number)
            if not bill_data:
                return False, "", f"Bill {bill_number} not found"

            # Check if printer is available
            if not self.printer.is_physical_printer_available():
                return False, "", "No physical printer detected. Please check printer connection."

            # Use the enhanced notepad printing method (most reliable for Brother printers)
            print(f"🖨️ Printing bill {bill_number} using enhanced notepad method...")

            success = self.printer.print_via_notepad(
                bill_data['bill_number'],
                bill_data['customer_name'],
                bill_data['items'],
                bill_data['total_amount'],
                bill_data['date'],
                bill_data['time']
            )

            if success:
                # Also save as PDF for backup
                pdf_path = self.printer.save_as_pdf(
                    bill_data['bill_number'],
                    bill_data['customer_name'],
                    bill_data['items'],
                    bill_data['total_amount'],
                    bill_data['date'],
                    bill_data['time']
                )

                return True, pdf_path or "", "✅ Bill printed successfully to your Brother printer!\n📄 PDF copy also saved for records."
            else:
                # Fallback to copy PRN method
                print("🔄 Notepad method failed, trying copy to PRN method...")

                success = self.printer.print_via_copy_prn(
                    bill_data['bill_number'],
                    bill_data['customer_name'],
                    bill_data['items'],
                    bill_data['total_amount'],
                    bill_data['date'],
                    bill_data['time']
                )

                if success:
                    return True, "", "✅ Bill printed successfully using alternative method!"
                else:
                    return False, "", "❌ Printing failed. Please check printer connection and try again."

        except Exception as e:
            return False, "", f"❌ Print error: {str(e)}"

    def enhanced_print_bill_with_options(self, bill_number: str) -> tuple:
        """
        Enhanced printing with multiple fallback options
        Returns: (success: bool, file_path: str, message: str)
        """
        try:
            # Get bill details
            bill_data = self.search_bill_by_number(bill_number)
            if not bill_data:
                return False, "", f"Bill {bill_number} not found"

            # Check printer availability first
            if not self.printer.is_physical_printer_available():
                # If no printer, save as PDF instead
                print("⚠️ No physical printer detected. Saving as PDF instead...")
                pdf_path = self.printer.save_as_pdf(
                    bill_data['bill_number'],
                    bill_data['customer_name'],
                    bill_data['items'],
                    bill_data['total_amount'],
                    bill_data['date'],
                    bill_data['time']
                )

                if pdf_path:
                    return True, pdf_path, "⚠️ No printer detected.\n📄 Bill saved as PDF instead.\nConnect printer and try printing again."
                else:
                    return False, "", "❌ No printer detected and PDF save failed."

            print(f"🖨️ Printing bill {bill_number} with enhanced methods...")

            # Method 1: Enhanced Notepad Printing (most reliable for Brother)
            success = self.printer.print_via_notepad(
                bill_data['bill_number'],
                bill_data['customer_name'],
                bill_data['items'],
                bill_data['total_amount'],
                bill_data['date'],
                bill_data['time']
            )

            if success:
                # Also save PDF backup
                pdf_path = self.printer.save_as_pdf(
                    bill_data['bill_number'],
                    bill_data['customer_name'],
                    bill_data['items'],
                    bill_data['total_amount'],
                    bill_data['date'],
                    bill_data['time']
                )
                return True, pdf_path or "", "✅ Bill printed successfully!\n📋 Check your Brother printer for the printed bill.\n📄 PDF backup also saved."

            # Method 2: Copy to PRN fallback
            print("🔄 Notepad method failed, trying direct printer method...")
            success = self.printer.print_via_copy_prn(
                bill_data['bill_number'],
                bill_data['customer_name'],
                bill_data['items'],
                bill_data['total_amount'],
                bill_data['date'],
                bill_data['time']
            )

            if success:
                return True, "", "✅ Bill printed using direct method!\n��� Check your printer for the printed bill."

            # Method 3: Standard printing fallback
            print("🔄 Direct method failed, trying standard printer method...")
            success = self.printer.print_to_printer(
                bill_data['bill_number'],
                bill_data['customer_name'],
                bill_data['items'],
                bill_data['total_amount'],
                bill_data['date'],
                bill_data['time']
            )

            if success:
                return True, "", "✅ Bill printed using standard method!"

            # All methods failed - save as PDF and show error
            print("❌ All printing methods failed. Saving as PDF...")
            pdf_path = self.printer.save_as_pdf(
                bill_data['bill_number'],
                bill_data['customer_name'],
                bill_data['items'],
                bill_data['total_amount'],
                bill_data['date'],
                bill_data['time']
            )

            if pdf_path:
                return False, pdf_path, "❌ Printing failed but bill saved as PDF.\n🔧 Please check printer connection and try again."
            else:
                return False, "", "❌ Printing failed and PDF save failed.\n🔧 Please check printer connection."

        except Exception as e:
            return False, "", f"❌ Print error: {str(e)}\n🔧 Please check printer connection and try again."

    def save_bill_as_pdf(self, bill_number: str) -> str:
        """Save bill as PDF file"""
        try:
            bill_data = self.search_bill_by_number(bill_number)
            if not bill_data:
                print(f"Bill {bill_number} not found")
                return None

            pdf_path = self.printer.save_as_pdf(
                bill_data['bill_number'],
                bill_data['customer_name'],
                bill_data['items'],
                bill_data['total_amount'],
                bill_data['date'],
                bill_data['time']
            )

            return pdf_path

        except Exception as e:
            print(f"Error saving PDF: {e}")
            return None

    def get_bill_details_for_display(self, bill_number: str) -> dict:
        """Get bill details formatted for display in GUI"""
        try:
            # Get bill details using existing search method
            bill_data = self.search_bill_by_number(bill_number)
            if not bill_data:
                return None

            # Format for GUI display
            formatted_data = {
                'bill_number': bill_data['bill_number'],
                'customer_name': bill_data['customer_name'],
                'customer_mobile': bill_data.get('customer_mobile', ''),
                'total_amount': bill_data['total_amount'],
                'date': bill_data['date'],
                'time': bill_data['time'],
                'payment_method': bill_data.get('payment_method', 'Cash'),
                'items': []
            }

            # Format items for display
            for item in bill_data['items']:
                formatted_data['items'].append({
                    'category': 'Food',  # You might want to add category to your database
                    'name': item['name'],
                    'quantity': item['quantity'],
                    'price': item['price'],
                    'total': item['total']
                })

            return formatted_data

        except Exception as e:
            print(f"Error getting bill details for display: {e}")
            return None

    # Legacy compatibility - keep old method name but use enhanced printing
    def print_or_save_bill(self, bill_number: str) -> tuple:
        """Legacy method - now uses enhanced printing"""
        return self.enhanced_print_bill_with_options(bill_number)
