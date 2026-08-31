"""
Bill Reports Module
Handles bill reporting and viewing functionality
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

class BillReports:
    """Manages bill reporting and viewing operations"""

    def __init__(self, root, billing_system, currency_symbol, show_bill_details_callback):
        self.root = root
        self.billing_system = billing_system
        self.currency = currency_symbol
        self.show_bill_details_callback = show_bill_details_callback

    def bills_by_date(self):
        """Show bills for a specific date"""
        date_str = simpledialog.askstring("Bills by Date", "Enter Date (YYYY-MM-DD):")
        if date_str:
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
                self.show_bills_window(date_str)
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")

    def show_bills_window(self, date_str):
        """Show bills in a new window"""
        bills = self.billing_system.get_bills_by_date(date_str)

        if not bills:
            messagebox.showinfo("No Bills", f"No bills found for {date_str}")
            return

        bills_window = tk.Toplevel(self.root)
        bills_window.title(f"Bills for {date_str}")

        # Make window responsive to screen size
        screen_width = bills_window.winfo_screenwidth()
        screen_height = bills_window.winfo_screenheight()

        # Calculate responsive window size
        window_width = min(max(900, int(screen_width * 0.7)), screen_width - 150)
        window_height = min(max(650, int(screen_height * 0.8)), screen_height - 100)

        bills_window.geometry(f"{window_width}x{window_height}")
        bills_window.resizable(True, True)  # Make window resizable
        bills_window.minsize(700, 500)    # Set minimum size

        # Center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        bills_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Configure window grid weights for responsiveness
        bills_window.columnconfigure(0, weight=1)
        bills_window.rowconfigure(0, weight=1)

        # Main container frame
        main_frame = ttk.Frame(bills_window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(0, weight=1)

        ttk.Label(header_frame, text=f"Bills for {date_str}",
                 font=('Arial', 14, 'bold')).pack()

        # Create treeview with responsive container
        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ('bill_number', 'customer', 'amount', 'time', 'payment_method')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        tree.heading('bill_number', text='Bill Number')
        tree.heading('customer', text='Customer')
        tree.heading('amount', text='Amount')
        tree.heading('time', text='Time')
        tree.heading('payment_method', text='Payment Method')

        # Configure columns to be responsive
        tree.column('bill_number', width=150, minwidth=120)
        tree.column('customer', width=180, minwidth=140)
        tree.column('amount', width=100, minwidth=80)
        tree.column('time', width=100, minwidth=80)
        tree.column('payment_method', width=120, minwidth=100)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Use grid for better responsiveness
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Add data
        total_sales = 0.0
        for bill in bills:
            tree.insert('', 'end', values=(
                bill['bill_number'],
                bill['customer_name'],
                f"₹{bill['total_amount']:.2f}",
                bill['time'],
                bill['payment_method']
            ))
            total_sales += bill['total_amount']

        # Add instruction and summary with responsive frames
        self._add_instructions_and_summary(main_frame, len(bills), total_sales)

        # Bind double-click to view bill details
        tree.bind('<Double-1>', lambda e: self._on_bill_double_click(tree))

    def view_all_bills(self):
        """View all bills"""
        bills = self.billing_system.get_all_bills()

        if not bills:
            messagebox.showinfo("No Bills", "No bills found")
            return

        bills_window = tk.Toplevel(self.root)
        bills_window.title("All Bills")

        # Make window responsive to screen size
        screen_width = bills_window.winfo_screenwidth()
        screen_height = bills_window.winfo_screenheight()

        # Calculate responsive window size
        window_width = min(max(1000, int(screen_width * 0.8)), screen_width - 100)
        window_height = min(max(700, int(screen_height * 0.85)), screen_height - 80)

        bills_window.geometry(f"{window_width}x{window_height}")
        bills_window.resizable(True, True)  # Make window resizable
        bills_window.minsize(800, 500)     # Set minimum size

        # Center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        bills_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Configure window grid weights for responsiveness
        bills_window.columnconfigure(0, weight=1)
        bills_window.rowconfigure(0, weight=1)

        # Main container frame
        main_frame = ttk.Frame(bills_window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(0, weight=1)

        ttk.Label(header_frame, text="All Bills",
                 font=('Arial', 14, 'bold')).pack()

        # Create treeview with responsive container
        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ('bill_number', 'customer', 'amount', 'date', 'time', 'payment_method')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        tree.heading('bill_number', text='Bill Number')
        tree.heading('customer', text='Customer')
        tree.heading('amount', text='Amount')
        tree.heading('date', text='Date')
        tree.heading('time', text='Time')
        tree.heading('payment_method', text='Payment Method')

        # Configure columns to be responsive
        tree.column('bill_number', width=140, minwidth=110)
        tree.column('customer', width=160, minwidth=130)
        tree.column('amount', width=100, minwidth=80)
        tree.column('date', width=110, minwidth=90)
        tree.column('time', width=90, minwidth=70)
        tree.column('payment_method', width=120, minwidth=100)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Use grid for better responsiveness
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Add data
        for bill in bills:
            tree.insert('', 'end', values=(
                bill['bill_number'],
                bill['customer_name'],
                f"₹{bill['total_amount']:.2f}",
                bill['date'],
                bill['time'],
                bill['payment_method']
            ))

        # Add double-click event handler
        tree.bind('<Double-1>', lambda event: self._on_bill_double_click(tree))

        # Add instruction and summary with responsive frames
        total_amount = sum(bill['total_amount'] for bill in bills)
        self._add_instructions_and_summary(main_frame, len(bills), total_amount)

    def sales_summary(self):
        """Show sales summary"""
        summary = self.billing_system.get_sales_summary()

        message = f"""Sales Summary
        
Total Bills: {summary['total_bills']}
Total Sales: ₹{summary['total_sales']:.2f}
Average Bill: ₹{summary['average_bill']:.2f}"""

        messagebox.showinfo("Sales Summary", message)

    def view_full_menu(self, food_manager):
        """View full menu"""
        menu_window = tk.Toplevel(self.root)
        menu_window.title("Full Menu")

        # Make window responsive to screen size
        screen_width = menu_window.winfo_screenwidth()
        screen_height = menu_window.winfo_screenheight()

        # Calculate responsive window size
        window_width = min(max(800, int(screen_width * 0.6)), screen_width - 200)
        window_height = min(max(750, int(screen_height * 0.85)), screen_height - 100)

        menu_window.geometry(f"{window_width}x{window_height}")
        menu_window.resizable(True, True)  # Make window resizable
        menu_window.minsize(600, 500)     # Set minimum size

        # Center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        menu_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Configure window grid weights for responsiveness
        menu_window.columnconfigure(0, weight=1)
        menu_window.rowconfigure(0, weight=1)

        # Main container frame
        main_frame = ttk.Frame(menu_window, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        header_frame.columnconfigure(0, weight=1)

        ttk.Label(header_frame, text="🍽️ Restaurant Menu",
                 font=('Arial', 16, 'bold')).pack()

        # Text display frame
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Arial', 11),
                             bg='white', fg='black', relief='sunken', bd=2)
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Add menu content
        categories = food_manager.get_categories()
        content = "🍽️ RESTAURANT MENU\n" + "="*50 + "\n\n"

        for category in categories:
            items = food_manager.get_items_by_category(category)
            if items:
                content += f"{category.upper()}\n"
                content += "-" * len(category) + "\n"

                for item in items:
                    status = "✓" if item['available'] else "✗"
                    content += f"{item['id']:2d}. {item['name']:<30} ₹{item['price']:>6.2f} {status}\n"

                content += "\n"

        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)

    def _on_bill_double_click(self, tree):
        """Handle double-click on bill item"""
        selection = tree.selection()
        if selection:
            item = tree.item(selection[0])
            bill_number = item['values'][0]

            bill_data = self.billing_system.get_bill_details_for_display(bill_number)
            if bill_data:
                self.show_bill_details_callback(bill_data)
            else:
                messagebox.showerror("Error", "Could not load bill details")

    def _add_instructions_and_summary(self, window, total_bills, total_sales):
        """Add instruction label and summary to bills window"""
        instruction_frame = ttk.Frame(window)
        instruction_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(instruction_frame, text="💡 Double-click on any bill to view complete details",
                 font=('Arial', 10, 'italic')).pack(anchor=tk.W)

        summary_frame = ttk.Frame(window)
        summary_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(summary_frame, text=f"Total Bills: {total_bills}",
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        ttk.Label(summary_frame, text=f"Total Sales: ₹{total_sales:.2f}",
                 font=('Arial', 10, 'bold')).pack(side=tk.RIGHT)
