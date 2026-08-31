"""
Order Management Module
Handles current order display and management functionality
"""
import tkinter as tk
from tkinter import ttk, messagebox

class OrderManager:
    """Manages the current order display and operations"""

    def __init__(self, parent, currency_symbol):
        self.parent = parent
        self.currency = currency_symbol
        self.current_order = []
        self.customer_var = None
        self.mobile_var = None
        self.order_tree = None
        self.total_label = None
        self.payment_method_var = None  # NEW: Track payment method

    def setup_order_display(self, middle_frame):
        """Setup the complete order management area with enhanced visibility and space utilization"""
        # Enhanced customer information section with better sizing for 1024x768
        customer_section = ttk.LabelFrame(middle_frame, text="Customer Information", padding="15")
        customer_section.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        customer_section.columnconfigure(1, weight=2)
        customer_section.columnconfigure(3, weight=1)

        # Customer name with much larger input field for better visibility
        ttk.Label(customer_section, text="Customer Name:", font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=6)
        self.customer_var = tk.StringVar()
        customer_entry = ttk.Entry(customer_section, textvariable=self.customer_var,
                                 font=('Arial', 12), width=25)
        customer_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 20), pady=6)
        customer_entry.bind('<KeyRelease>', self._on_customer_name_change)
        customer_entry.bind('<FocusOut>', self._on_customer_name_change)

        # Mobile number with larger input field and better styling
        ttk.Label(customer_section, text="Mobile:", font=('Arial', 11, 'bold')).grid(row=0, column=2, sticky=tk.W, pady=6)
        self.mobile_var = tk.StringVar()
        mobile_entry = ttk.Entry(customer_section, textvariable=self.mobile_var,
                               font=('Arial', 12), width=15)
        mobile_entry.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(10, 0), pady=6)
        mobile_entry.bind('<KeyPress>', self._validate_mobile_input)
        mobile_entry.bind('<KeyRelease>', self._on_mobile_change)

        # Payment method selection - NEW ADDITION
        ttk.Label(customer_section, text="Payment:", font=('Arial', 11, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=6)
        self.payment_method_var = tk.StringVar(value="Cash")
        payment_combo = ttk.Combobox(customer_section, textvariable=self.payment_method_var,
                                   font=('Arial', 12), width=12, state="readonly")
        payment_combo['values'] = ('Cash', 'UPI', 'Card', 'Bank Transfer', 'Other')
        payment_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 20), pady=6)

        # Add payment status indicator
        self.payment_status_label = ttk.Label(customer_section, text="💵 Cash Payment",
                                            font=('Arial', 10), foreground='green')
        self.payment_status_label.grid(row=1, column=2, columnspan=2, sticky=tk.W, padx=(10, 0), pady=6)

        # Bind payment method change
        payment_combo.bind('<<ComboboxSelected>>', self._on_payment_method_change)

        # Enhanced order items display with optimized height for 1024x768 - moved up to row 1
        order_display_frame = ttk.LabelFrame(middle_frame, text="Order Items", padding="10")
        order_display_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        order_display_frame.columnconfigure(0, weight=1)
        order_display_frame.rowconfigure(0, weight=1)

        # Configure treeview with reduced height to ensure order summary is visible
        columns = ('item', 'qty', 'price', 'total')
        self.order_tree = ttk.Treeview(order_display_frame, columns=columns, show='headings', height=8)

        # Optimized column headers and widths for better visibility
        self.order_tree.heading('item', text='Item Name')
        self.order_tree.heading('qty', text='Qty')
        self.order_tree.heading('price', text='Unit Price')
        self.order_tree.heading('total', text='Total')

        # Better column widths optimized for 1024x768 resolution
        self.order_tree.column('item', width=180, minwidth=150)
        self.order_tree.column('qty', width=50, minwidth=40)
        self.order_tree.column('price', width=80, minwidth=70)
        self.order_tree.column('total', width=80, minwidth=70)

        # Enhanced scrollbar
        order_scrollbar = ttk.Scrollbar(order_display_frame, orient="vertical", command=self.order_tree.yview)
        self.order_tree.configure(yscrollcommand=order_scrollbar.set)

        self.order_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        order_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Compact order controls with reduced padding
        order_controls = ttk.LabelFrame(middle_frame, text="Order Actions", padding="5")
        order_controls.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        order_controls.columnconfigure(0, weight=1)
        order_controls.columnconfigure(1, weight=1)
        order_controls.columnconfigure(2, weight=1)

        ttk.Button(order_controls, text="➖ Remove", command=self.remove_item,
                  style='Action.TButton').grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 3), pady=2)
        ttk.Button(order_controls, text="🔄 Update Qty", command=self.update_quantity,
                  style='Action.TButton').grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(3, 3), pady=2)
        ttk.Button(order_controls, text="🗑️ Clear All", command=self.clear_order,
                  style='Action.TButton').grid(row=0, column=2, sticky=(tk.W, tk.E), padx=(3, 0), pady=2)

        # Compact total display that fits within screen bounds
        total_section = ttk.LabelFrame(middle_frame, text="Order Summary", padding="8")
        total_section.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        total_section.columnconfigure(0, weight=1)
        total_section.columnconfigure(1, weight=1)

        # More visible summary layout
        self.item_count_label = ttk.Label(total_section, text="Items: 0",
                                        font=('Arial', 12, 'bold'), foreground='#2E8B57')
        self.item_count_label.grid(row=0, column=0, sticky=tk.W, padx=5)

        self.total_label = ttk.Label(total_section, text="Total: ₹0.00",
                                   font=('Arial', 16, 'bold'), foreground='#d63384')
        self.total_label.grid(row=0, column=1, sticky=tk.E, padx=5)

    def add_item_to_order(self, item):
        """Add an item to the current order"""
        # Check if item is already in the order
        for order_item in self.current_order:
            if order_item['id'] == item['id']:
                # Increase quantity
                order_item['quantity'] += 1
                self.refresh_order_display()
                return

        # Add new item to order
        self.current_order.append({
            'id': item['id'],
            'name': item['name'],
            'price': item['price'],
            'quantity': 1
        })
        self.refresh_order_display()

    def remove_item(self):
        """Remove selected item from order"""
        selected = self.order_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to remove")
            return

        item_index = self.order_tree.index(selected[0])
        self.current_order.pop(item_index)
        self.refresh_order_display()

    def clear_order(self):
        """Clear the current order"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the order?"):
            self.current_order = []
            self.customer_var.set("")
            self.mobile_var.set("")
            self.refresh_order_display()

    def refresh_order_display(self):
        """Refresh the order display"""
        # Clear existing items
        for item in self.order_tree.get_children():
            self.order_tree.delete(item)

        total = 0.0
        item_count = 0

        # Add items to treeview
        for order_item in self.current_order:
            item_total = order_item['price'] * order_item['quantity']
            total += item_total
            item_count += order_item['quantity']

            self.order_tree.insert('', 'end', values=(
                order_item['name'],
                order_item['quantity'],
                f"₹{order_item['price']:.2f}",
                f"₹{item_total:.2f}"
            ))

        # Update total and item count
        self.total_label.config(text=f"Total: ₹{total:.2f}")
        self.item_count_label.config(text=f"Items: {item_count}")

    def update_quantity(self):
        """Update quantity of selected item"""
        selected = self.order_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to update quantity")
            return

        item_index = self.order_tree.index(selected[0])
        current_item = self.current_order[item_index]

        # Create a simple dialog for quantity input with better sizing
        dialog = tk.Toplevel(self.parent)
        dialog.title("Update Quantity")
        dialog.geometry("400x180")  # Increased width and height for better button visibility
        dialog.resizable(False, False)
        dialog.transient(self.parent)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        # Dialog content with better spacing
        ttk.Label(dialog, text=f"Item: {current_item['name']}", font=('Arial', 11, 'bold')).pack(pady=(15, 10))
        ttk.Label(dialog, text="New Quantity:", font=('Arial', 10)).pack(pady=(0, 5))

        qty_var = tk.StringVar(value=str(current_item['quantity']))
        qty_entry = ttk.Entry(dialog, textvariable=qty_var, font=('Arial', 12), width=10, justify='center')
        qty_entry.pack(pady=5)
        qty_entry.select_range(0, tk.END)
        qty_entry.focus()

        # Buttons with improved layout and spacing
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20, fill='x', padx=20)

        def update_qty():
            try:
                new_qty = int(qty_var.get())
                if new_qty <= 0:
                    messagebox.showwarning("Invalid Quantity", "Quantity must be greater than 0")
                    return
                elif new_qty > 99:
                    messagebox.showwarning("Invalid Quantity", "Quantity cannot exceed 99")
                    return

                current_item['quantity'] = new_qty
                self.refresh_order_display()
                dialog.destroy()
            except ValueError:
                messagebox.showwarning("Invalid Input", "Please enter a valid number")

        def remove_item():
            self.current_order.pop(item_index)
            self.refresh_order_display()
            dialog.destroy()

        # Create buttons with better spacing and sizing
        update_btn = ttk.Button(button_frame, text="Update", command=update_qty, width=12)
        update_btn.pack(side=tk.LEFT, padx=(0, 5))

        remove_btn = ttk.Button(button_frame, text="Remove Item", command=remove_item, width=12)
        remove_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = ttk.Button(button_frame, text="Cancel", command=dialog.destroy, width=12)
        cancel_btn.pack(side=tk.LEFT, padx=(5, 0))

        # Bind Enter key to update
        dialog.bind('<Return>', lambda e: update_qty())

    def get_customer_info(self):
        """Get customer name, mobile, and payment method"""
        return {
            'name': self.customer_var.get().strip(),
            'mobile': self.mobile_var.get().strip(),
            'payment_method': self.payment_method_var.get() if self.payment_method_var else 'Cash'
        }

    def get_order_items(self):
        """Get current order items in the format needed by billing system"""
        return [{
            'item_id': item['id'],
            'quantity': item['quantity']
        } for item in self.current_order]

    def has_items(self):
        """Check if there are items in the order"""
        return len(self.current_order) > 0

    def _on_customer_name_change(self, event=None):
        """Auto-capitalize customer name - first letter of each word"""
        current_position = event.widget.index(tk.INSERT) if event and hasattr(event, 'widget') else 0
        name = self.customer_var.get()

        # Capitalize first letter of each word
        capitalized_name = ' '.join(word.capitalize() for word in name.split(' '))

        # Set the value without triggering another event
        self.customer_var.set(capitalized_name)

        # Restore cursor position if possible
        if event and hasattr(event, 'widget'):
            try:
                event.widget.icursor(current_position)
            except:
                pass

    def _validate_mobile_input(self, event):
        """Validate mobile number input - only allow digits and limit to 10 digits"""
        # Allow backspace, delete, and arrow keys
        if event.keysym in ['BackSpace', 'Delete', 'Left', 'Right', 'Tab']:
            return True

        # Get current text and what it would be after this keypress
        current_text = self.mobile_var.get()

        # Only allow digits
        if not event.char.isdigit():
            return "break"  # Prevent the character from being entered

        # Check if adding this digit would exceed 10 digits
        if len(current_text) >= 10:
            return "break"  # Prevent the character from being entered

        return True

    def _on_mobile_change(self, event=None):
        """Handle mobile number changes"""
        mobile = self.mobile_var.get()

        # Remove any non-digit characters (in case of paste)
        digits_only = ''.join(filter(str.isdigit, mobile))

        # Limit to 10 digits
        if len(digits_only) > 10:
            digits_only = digits_only[:10]

        # Update the field with digits only
        if digits_only != mobile:
            self.mobile_var.set(digits_only)

    def _on_payment_method_change(self, event=None):
        """Update payment status label based on selected payment method"""
        payment_method = self.payment_method_var.get()
        if payment_method == "Cash":
            self.payment_status_label.config(text="💵 Cash Payment", foreground='green')
        elif payment_method == "UPI":
            self.payment_status_label.config(text="📱 UPI Payment", foreground='blue')
        elif payment_method == "Card":
            self.payment_status_label.config(text="💳 Card Payment", foreground='orange')
        elif payment_method == "Bank Transfer":
            self.payment_status_label.config(text="🏦 Bank Transfer", foreground='purple')
        else:
            self.payment_status_label.config(text="Other Payment", foreground='red')

    def validate_customer_info(self):
        """Validate customer information before bill generation"""
        customer_info = self.get_customer_info()

        # Check if customer name is provided
        if not customer_info['name']:
            messagebox.showwarning("Validation Error", "Please enter customer name")
            return False

        # Check if mobile number is provided and valid
        if not customer_info['mobile']:
            messagebox.showwarning("Validation Error", "Please enter mobile number (required)")
            return False

        # Check if mobile number has exactly 10 digits
        if len(customer_info['mobile']) != 10:
            messagebox.showwarning("Validation Error", "Mobile number must be exactly 10 digits")
            return False

        return True
