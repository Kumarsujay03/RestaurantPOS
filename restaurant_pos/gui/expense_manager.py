"""
Expense Management Module
Handles expense tracking, categorization, and profit/loss analysis
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import sqlite3
import os
from restaurant_pos.core.config import get_currency_symbol

class ExpenseManager:
    """Manages restaurant expenses and profit/loss calculations"""

    def __init__(self, parent):
        self.parent = parent
        self.currency = get_currency_symbol()
        # Use the same database path as other modules - in the current directory
        self.db_path = "restaurant.db"
        self._initialize_database()

    def _initialize_database(self):
        """Initialize expense tracking tables in the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create expenses table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    amount REAL NOT NULL,
                    payment_method TEXT DEFAULT 'Cash',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create expense categories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS expense_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Insert default categories if they don't exist
            default_categories = [
                ('Raw Materials', 'Food ingredients and cooking supplies'),
                ('Utilities', 'Electricity, water, gas bills'),
                ('Rent', 'Restaurant rent and property costs'),
                ('Staff Salary', 'Employee wages and benefits'),
                ('Equipment', 'Kitchen equipment and maintenance'),
                ('Marketing', 'Advertising and promotional costs'),
                ('Transportation', 'Delivery and transport costs'),
                ('Miscellaneous', 'Other business expenses')
            ]

            cursor.executemany('''
                INSERT OR IGNORE INTO expense_categories (name, description)
                VALUES (?, ?)
            ''', default_categories)

            conn.commit()
            conn.close()
            print("✅ Expense database initialized successfully")

        except Exception as e:
            print(f"❌ Error initializing expense database: {e}")
            messagebox.showerror("Database Error", f"Failed to initialize expense database: {e}")

    def show_expense_window(self):
        """Show the main expense management window"""
        # Re-initialize database to ensure tables exist
        self._initialize_database()

        self.expense_window = tk.Toplevel(self.parent)
        self.expense_window.title("💰 Expense Management")
        self.expense_window.geometry("1000x700")
        self.expense_window.resizable(True, True)

        # Configure grid weights
        self.expense_window.columnconfigure(0, weight=1)
        self.expense_window.rowconfigure(0, weight=1)

        # Create main notebook for tabs
        notebook = ttk.Notebook(self.expense_window)
        notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)

        # Create tabs
        self._create_add_expense_tab(notebook)
        self._create_view_expenses_tab(notebook)
        self._create_categories_tab(notebook)
        self._create_profit_loss_tab(notebook)

        # Load categories and expenses after creating all tabs
        self._load_categories()
        if hasattr(self, 'expenses_tree'):
            self._load_expenses()

    def _create_add_expense_tab(self, notebook):
        """Create the add expense tab"""
        add_frame = ttk.Frame(notebook, padding="20")
        notebook.add(add_frame, text="➕ Add Expense")

        # Configure grid
        add_frame.columnconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(add_frame, text="Add New Expense",
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Date selection
        ttk.Label(add_frame, text="Date:", font=('Arial', 11, 'bold')).grid(
            row=1, column=0, sticky=tk.W, pady=5)

        date_frame = ttk.Frame(add_frame)
        date_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

        self.expense_date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_entry = ttk.Entry(date_frame, textvariable=self.expense_date, width=15)
        date_entry.grid(row=0, column=0, sticky=tk.W)

        ttk.Button(date_frame, text="Today",
                  command=lambda: self.expense_date.set(datetime.now().strftime("%Y-%m-%d"))
                  ).grid(row=0, column=1, padx=(10, 0))

        # Category selection
        ttk.Label(add_frame, text="Category:", font=('Arial', 11, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=5)

        self.expense_category = ttk.Combobox(add_frame, width=30)
        self.expense_category.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        self._load_categories()

        # Description
        ttk.Label(add_frame, text="Description:", font=('Arial', 11, 'bold')).grid(
            row=3, column=0, sticky=tk.W, pady=5)

        self.expense_description = ttk.Entry(add_frame, width=50)
        self.expense_description.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)

        # Amount
        ttk.Label(add_frame, text="Amount:", font=('Arial', 11, 'bold')).grid(
            row=4, column=0, sticky=tk.W, pady=5)

        amount_frame = ttk.Frame(add_frame)
        amount_frame.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(amount_frame, text=self.currency, font=('Arial', 11)).grid(
            row=0, column=0, sticky=tk.W)

        self.expense_amount = ttk.Entry(amount_frame, width=15)
        self.expense_amount.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))

        # Payment method
        ttk.Label(add_frame, text="Payment Method:", font=('Arial', 11, 'bold')).grid(
            row=5, column=0, sticky=tk.W, pady=5)

        self.expense_payment = ttk.Combobox(add_frame, values=[
            'Cash', 'Card', 'Bank Transfer', 'UPI', 'Cheque', 'Other'
        ], width=20)
        self.expense_payment.set('Cash')
        self.expense_payment.grid(row=5, column=1, sticky=tk.W, pady=5)

        # Notes
        ttk.Label(add_frame, text="Notes:", font=('Arial', 11, 'bold')).grid(
            row=6, column=0, sticky=(tk.W, tk.N), pady=5)

        self.expense_notes = tk.Text(add_frame, height=4, width=50)
        self.expense_notes.grid(row=6, column=1, sticky=(tk.W, tk.E), pady=5)

        # Buttons
        button_frame = ttk.Frame(add_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="💾 Save Expense",
                  command=self._save_expense).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(button_frame, text="🗑️ Clear Form",
                  command=self._clear_expense_form).pack(side=tk.LEFT, padx=(0, 10))

    def _create_view_expenses_tab(self, notebook):
        """Create the view expenses tab"""
        view_frame = ttk.Frame(notebook, padding="10")
        notebook.add(view_frame, text="📋 View Expenses")

        # Configure grid
        view_frame.columnconfigure(0, weight=1)
        view_frame.rowconfigure(1, weight=1)

        # Filters frame
        filter_frame = ttk.LabelFrame(view_frame, text="Filters", padding="10")
        filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        filter_frame.columnconfigure(3, weight=1)

        # Date filter
        ttk.Label(filter_frame, text="From:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))

        self.filter_from_date = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        ttk.Entry(filter_frame, textvariable=self.filter_from_date, width=12).grid(
            row=0, column=1, padx=(0, 10))

        ttk.Label(filter_frame, text="To:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))

        self.filter_to_date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(filter_frame, textvariable=self.filter_to_date, width=12).grid(
            row=0, column=3, padx=(0, 10))

        # Category filter
        ttk.Label(filter_frame, text="Category:").grid(row=0, column=4, sticky=tk.W, padx=(10, 5))

        self.filter_category = ttk.Combobox(filter_frame, width=15)
        self.filter_category.grid(row=0, column=5, padx=(0, 10))

        # Filter button
        ttk.Button(filter_frame, text="🔍 Filter",
                  command=self._filter_expenses).grid(row=0, column=6, padx=(10, 0))

        # Expenses treeview
        tree_frame = ttk.Frame(view_frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ('Date', 'Category', 'Description', 'Amount', 'Payment', 'Notes')
        self.expenses_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)

        # Configure columns
        self.expenses_tree.heading('Date', text='Date')
        self.expenses_tree.heading('Category', text='Category')
        self.expenses_tree.heading('Description', text='Description')
        self.expenses_tree.heading('Amount', text='Amount')
        self.expenses_tree.heading('Payment', text='Payment')
        self.expenses_tree.heading('Notes', text='Notes')

        self.expenses_tree.column('Date', width=100)
        self.expenses_tree.column('Category', width=120)
        self.expenses_tree.column('Description', width=200)
        self.expenses_tree.column('Amount', width=100)
        self.expenses_tree.column('Payment', width=100)
        self.expenses_tree.column('Notes', width=150)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.expenses_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.expenses_tree.xview)

        self.expenses_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Grid treeview and scrollbars
        self.expenses_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Action buttons
        action_frame = ttk.Frame(view_frame)
        action_frame.grid(row=2, column=0, pady=10)

        ttk.Button(action_frame, text="✏️ Edit Selected",
                  command=self._edit_expense).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(action_frame, text="🗑️ Delete Selected",
                  command=self._delete_expense).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(action_frame, text="📊 Export to CSV",
                  command=self._export_expenses).pack(side=tk.LEFT)

        # Load initial data
        self._load_expenses()

    def _create_categories_tab(self, notebook):
        """Create the categories management tab"""
        cat_frame = ttk.Frame(notebook, padding="20")
        notebook.add(cat_frame, text="🏷️ Categories")

        # Add new category section
        add_cat_frame = ttk.LabelFrame(cat_frame, text="Add New Category", padding="10")
        add_cat_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        add_cat_frame.columnconfigure(1, weight=1)

        ttk.Label(add_cat_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.new_category_name = ttk.Entry(add_cat_frame, width=30)
        self.new_category_name.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))

        ttk.Button(add_cat_frame, text="➕ Add Category",
                  command=self._add_category).grid(row=0, column=2)

        # Categories list
        list_frame = ttk.LabelFrame(cat_frame, text="Existing Categories", padding="10")
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        self.categories_listbox = tk.Listbox(list_frame, height=15)
        self.categories_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        cat_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.categories_listbox.yview)
        cat_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.categories_listbox.configure(yscrollcommand=cat_scrollbar.set)

        # Category buttons
        cat_button_frame = ttk.Frame(list_frame)
        cat_button_frame.grid(row=1, column=0, pady=10)

        ttk.Button(cat_button_frame, text="🗑️ Delete Selected",
                  command=self._delete_category).pack(side=tk.LEFT)

        self._load_categories_list()

    def _create_profit_loss_tab(self, notebook):
        """Create the profit/loss analysis tab"""
        pl_frame = ttk.Frame(notebook, padding="20")
        notebook.add(pl_frame, text="📊 Profit/Loss Analysis")

        # Date range selection
        range_frame = ttk.LabelFrame(pl_frame, text="Analysis Period", padding="10")
        range_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

        ttk.Label(range_frame, text="From:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))

        self.pl_from_date = tk.StringVar(value=(datetime.now().replace(day=1)).strftime("%Y-%m-%d"))
        ttk.Entry(range_frame, textvariable=self.pl_from_date, width=12).grid(
            row=0, column=1, padx=(0, 10))

        ttk.Label(range_frame, text="To:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))

        self.pl_to_date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(range_frame, textvariable=self.pl_to_date, width=12).grid(
            row=0, column=3, padx=(0, 10))

        ttk.Button(range_frame, text="📊 Generate Report",
                  command=self._generate_profit_loss_report).grid(row=0, column=4, padx=(20, 0))

        # Quick period buttons
        quick_frame = ttk.Frame(range_frame)
        quick_frame.grid(row=1, column=0, columnspan=5, pady=(10, 0))

        ttk.Button(quick_frame, text="This Month",
                  command=self._set_current_month).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(quick_frame, text="Last Month",
                  command=self._set_last_month).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(quick_frame, text="Last 3 Months",
                  command=self._set_last_3_months).pack(side=tk.LEFT)

        # Results frame
        self.results_frame = ttk.LabelFrame(pl_frame, text="Financial Summary", padding="20")
        self.results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.results_frame.columnconfigure(0, weight=1)

    def _load_categories(self):
        """Load categories for the combobox"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM expense_categories ORDER BY name")
            categories = [row[0] for row in cursor.fetchall()]

            self.expense_category['values'] = categories
            if hasattr(self, 'filter_category'):
                self.filter_category['values'] = ['All'] + categories
                self.filter_category.set('All')

            conn.close()
        except Exception as e:
            print(f"Error loading categories: {e}")

    def _save_expense(self):
        """Save a new expense to the database"""
        try:
            # Validate inputs
            if not self.expense_category.get():
                messagebox.showerror("Error", "Please select a category")
                return

            if not self.expense_description.get().strip():
                messagebox.showerror("Error", "Please enter a description")
                return

            try:
                amount = float(self.expense_amount.get())
                if amount <= 0:
                    raise ValueError("Amount must be positive")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount")
                return

            # Save to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO expenses (date, category, description, amount, payment_method, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                self.expense_date.get(),
                self.expense_category.get(),
                self.expense_description.get().strip(),
                amount,
                self.expense_payment.get(),
                self.expense_notes.get('1.0', tk.END).strip()
            ))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Expense of {self.currency}{amount:.2f} saved successfully!")
            self._clear_expense_form()

            # Refresh expenses view if it exists
            if hasattr(self, 'expenses_tree'):
                self._load_expenses()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save expense: {e}")

    def _clear_expense_form(self):
        """Clear the expense form"""
        self.expense_date.set(datetime.now().strftime("%Y-%m-%d"))
        self.expense_category.set('')
        self.expense_description.delete(0, tk.END)
        self.expense_amount.delete(0, tk.END)
        self.expense_payment.set('Cash')
        self.expense_notes.delete('1.0', tk.END)

    def _load_expenses(self):
        """Load expenses into the treeview"""
        try:
            # Clear existing items
            for item in self.expenses_tree.get_children():
                self.expenses_tree.delete(item)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Apply filters
            query = "SELECT date, category, description, amount, payment_method, notes FROM expenses WHERE 1=1"
            params = []

            if hasattr(self, 'filter_from_date'):
                query += " AND date >= ?"
                params.append(self.filter_from_date.get())

            if hasattr(self, 'filter_to_date'):
                query += " AND date <= ?"
                params.append(self.filter_to_date.get())

            if hasattr(self, 'filter_category') and self.filter_category.get() != 'All':
                query += " AND category = ?"
                params.append(self.filter_category.get())

            query += " ORDER BY date DESC"

            cursor.execute(query, params)
            expenses = cursor.fetchall()

            total_amount = 0
            for expense in expenses:
                date, category, description, amount, payment, notes = expense
                total_amount += amount

                # Format amount with currency
                formatted_amount = f"{self.currency}{amount:.2f}"

                self.expenses_tree.insert('', 'end', values=(
                    date, category, description, formatted_amount, payment, notes or ''
                ))

            conn.close()

            # Update status
            if hasattr(self, 'expenses_tree'):
                # Add total at the bottom (you can implement this if needed)
                pass

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load expenses: {e}")

    def _filter_expenses(self):
        """Apply filters and reload expenses"""
        self._load_expenses()

    def _add_category(self):
        """Add a new expense category"""
        category_name = self.new_category_name.get().strip()

        if not category_name:
            messagebox.showerror("Error", "Please enter a category name")
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("INSERT INTO expense_categories (name) VALUES (?)", (category_name,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Category '{category_name}' added successfully!")
            self.new_category_name.delete(0, tk.END)
            self._load_categories()
            self._load_categories_list()

        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Category already exists")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add category: {e}")

    def _load_categories_list(self):
        """Load categories into the listbox"""
        try:
            self.categories_listbox.delete(0, tk.END)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM expense_categories ORDER BY name")

            for row in cursor.fetchall():
                self.categories_listbox.insert(tk.END, row[0])

            conn.close()
        except Exception as e:
            print(f"Error loading categories list: {e}")

    def _delete_category(self):
        """Delete selected category"""
        selection = self.categories_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a category to delete")
            return

        category_name = self.categories_listbox.get(selection[0])

        if messagebox.askyesno("Confirm Delete", f"Delete category '{category_name}'?\n\nNote: This will not delete existing expenses in this category."):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM expense_categories WHERE name = ?", (category_name,))
                conn.commit()
                conn.close()

                self._load_categories()
                self._load_categories_list()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete category: {e}")

    def _generate_profit_loss_report(self):
        """Generate profit/loss report for the selected period"""
        try:
            from_date = self.pl_from_date.get()
            to_date = self.pl_to_date.get()

            # Clear previous results
            for widget in self.results_frame.winfo_children():
                widget.destroy()

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get total revenue from bills
            cursor.execute('''
                SELECT COALESCE(SUM(total_amount), 0) 
                FROM bills 
                WHERE date BETWEEN ? AND ?
            ''', (from_date, to_date))

            total_revenue = cursor.fetchone()[0]

            # Get total expenses by category
            cursor.execute('''
                SELECT category, SUM(amount) 
                FROM expenses 
                WHERE date BETWEEN ? AND ?
                GROUP BY category
                ORDER BY SUM(amount) DESC
            ''', (from_date, to_date))

            expense_by_category = cursor.fetchall()
            total_expenses = sum(amount for _, amount in expense_by_category)

            # Calculate profit/loss
            profit_loss = total_revenue - total_expenses

            conn.close()

            # Display results
            title_label = ttk.Label(self.results_frame,
                                   text=f"Financial Report: {from_date} to {to_date}",
                                   font=('Arial', 14, 'bold'))
            title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

            # Revenue section
            revenue_frame = ttk.LabelFrame(self.results_frame, text="Revenue", padding="10")
            revenue_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 10))

            ttk.Label(revenue_frame, text=f"Total Sales: {self.currency}{total_revenue:.2f}",
                     font=('Arial', 12, 'bold'), foreground='green').pack()

            # Expenses section
            expenses_frame = ttk.LabelFrame(self.results_frame, text="Expenses by Category", padding="10")
            expenses_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 10))

            for category, amount in expense_by_category:
                ttk.Label(expenses_frame,
                         text=f"{category}: {self.currency}{amount:.2f}").pack(anchor=tk.W)

            ttk.Label(expenses_frame, text=f"Total Expenses: {self.currency}{total_expenses:.2f}",
                     font=('Arial', 11, 'bold'), foreground='red').pack(pady=(10, 0))

            # Profit/Loss section
            pl_frame = ttk.LabelFrame(self.results_frame, text="Profit/Loss", padding="10")
            pl_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

            color = 'green' if profit_loss >= 0 else 'red'
            status = 'Profit' if profit_loss >= 0 else 'Loss'

            ttk.Label(pl_frame,
                     text=f"Net {status}: {self.currency}{abs(profit_loss):.2f}",
                     font=('Arial', 14, 'bold'), foreground=color).pack()

            # Profit margin
            if total_revenue > 0:
                margin = (profit_loss / total_revenue) * 100
                ttk.Label(pl_frame,
                         text=f"Profit Margin: {margin:.1f}%",
                         font=('Arial', 11)).pack()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")

    def _set_current_month(self):
        """Set date range to current month"""
        today = datetime.now()
        first_day = today.replace(day=1)
        self.pl_from_date.set(first_day.strftime("%Y-%m-%d"))
        self.pl_to_date.set(today.strftime("%Y-%m-%d"))

    def _set_last_month(self):
        """Set date range to last month"""
        today = datetime.now()
        first_day_this_month = today.replace(day=1)
        last_day_last_month = first_day_this_month - timedelta(days=1)
        first_day_last_month = last_day_last_month.replace(day=1)

        self.pl_from_date.set(first_day_last_month.strftime("%Y-%m-%d"))
        self.pl_to_date.set(last_day_last_month.strftime("%Y-%m-%d"))

    def _set_last_3_months(self):
        """Set date range to last 3 months"""
        today = datetime.now()
        three_months_ago = today - timedelta(days=90)

        self.pl_from_date.set(three_months_ago.strftime("%Y-%m-%d"))
        self.pl_to_date.set(today.strftime("%Y-%m-%d"))

    def _edit_expense(self):
        """Edit selected expense (placeholder for future implementation)"""
        selection = self.expenses_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an expense to edit")
            return

        messagebox.showinfo("Info", "Edit functionality will be implemented in future updates")

    def _delete_expense(self):
        """Delete selected expense (placeholder for future implementation)"""
        selection = self.expenses_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an expense to delete")
            return

        messagebox.showinfo("Info", "Delete functionality will be implemented in future updates")

    def _export_expenses(self):
        """Export expenses to CSV (placeholder for future implementation)"""
        messagebox.showinfo("Info", "CSV export functionality will be implemented in future updates")
