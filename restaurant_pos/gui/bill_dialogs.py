"""
Bill Dialog Module
Handles all bill-related dialog windows and operations
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from restaurant_pos.core.config import get_full_restaurant_info

class BillDialogs:
    """Manages all bill-related dialog windows"""

    def __init__(self, root, billing_system, currency_symbol):
        self.root = root
        self.billing_system = billing_system
        self.currency = currency_symbol

    def show_bill_success_dialog(self, bill_number, clear_order_callback):
        """Show bill success dialog with printing options"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Bill Generated Successfully")

        # Make dialog responsive to screen size
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()

        # Calculate responsive dialog size
        dialog_width = min(max(500, int(screen_width * 0.4)), 600)
        dialog_height = min(max(350, int(screen_height * 0.5)), 450)

        dialog.geometry(f"{dialog_width}x{dialog_height}")
        dialog.minsize(450, 300)  # Set minimum size
        dialog.resizable(True, True)  # Make resizable

        dialog.transient(self.root)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog_width) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog_height) // 2
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        # Configure dialog grid for responsiveness
        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)

        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)  # Make button area expandable

        # Success message
        ttk.Label(main_frame, text="✅ Bill generated successfully!",
                 font=('Arial', 14, 'bold')).grid(row=0, column=0, pady=(0, 15))

        ttk.Label(main_frame, text=f"Bill Number: {bill_number}",
                 font=('Arial', 11)).grid(row=1, column=0, pady=(0, 20))

        # Print options section
        print_label = ttk.Label(main_frame, text="Print Options:",
                               font=('Arial', 11, 'bold'))
        print_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 10))

        # Print options buttons with responsive grid
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)

        ttk.Button(button_frame, text="🖨️ Print Bill",
                  command=lambda: self._print_bill_and_clear(bill_number, dialog, clear_order_callback),
                  style='Action.TButton').grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))

        ttk.Button(button_frame, text="💾 Save as PDF",
                  command=lambda: self._save_pdf_and_clear(bill_number, dialog, clear_order_callback),
                  style='Action.TButton').grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))

        ttk.Button(button_frame, text="👁️ View Bill",
                  command=lambda: self._view_bill_and_clear(bill_number, dialog, clear_order_callback),
                  style='Action.TButton').grid(row=0, column=2, padx=5, pady=5, sticky=(tk.W, tk.E))

        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        # Order management section
        order_label = ttk.Label(main_frame, text="Order Management:",
                               font=('Arial', 11, 'bold'))
        order_label.grid(row=5, column=0, sticky=tk.W, pady=(0, 10))

        # Order management buttons with responsive grid
        order_frame = ttk.Frame(main_frame)
        order_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        order_frame.columnconfigure(0, weight=1)
        order_frame.columnconfigure(1, weight=1)

        ttk.Button(order_frame, text="Skip Print & Clear Order",
                  command=lambda: self._clear_order_and_close(dialog, clear_order_callback),
                  style='Action.TButton').grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))

        ttk.Button(order_frame, text="Close (Keep Order)",
                  command=dialog.destroy,
                  style='Action.TButton').grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))

    def show_bill_details_window(self, bill_data):
        """Show detailed bill information in a new window"""
        bill_window = tk.Toplevel(self.root)
        bill_window.title(f"Bill Details - {bill_data['bill_number']}")
        bill_window.geometry("800x800")
        bill_window.resizable(True, True)
        bill_window.minsize(700, 600)

        # Configure window grid weights for auto-resizing
        bill_window.columnconfigure(0, weight=1)
        bill_window.rowconfigure(0, weight=1)

        # Main frame
        main_frame = ttk.Frame(bill_window, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)

        self._create_bill_header(main_frame)
        self._create_bill_info(main_frame, bill_data)
        self._create_order_details(main_frame, bill_data)
        self._create_bill_summary(main_frame, bill_data)
        self._create_action_buttons(main_frame, bill_data, bill_window)

    def _create_bill_header(self, main_frame):
        """Create restaurant header section"""
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(0, weight=1)

        restaurant_info = get_full_restaurant_info()

        ttk.Label(header_frame, text=restaurant_info['name'],
                 font=('Arial', 18, 'bold')).pack()
        ttk.Label(header_frame, text=restaurant_info['address'],
                 font=('Arial', 10)).pack()
        ttk.Label(header_frame, text=f"Phone: {restaurant_info['phone']}",
                 font=('Arial', 10)).pack()

        ttk.Separator(main_frame, orient='horizontal').grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)

    def _create_bill_info(self, main_frame, bill_data):
        """Create bill information section"""
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(0, weight=1)
        info_frame.columnconfigure(1, weight=1)

        # Left side - Bill details
        left_info = ttk.Frame(info_frame)
        left_info.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        ttk.Label(left_info, text="Bill Information",
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        ttk.Label(left_info, text=f"Bill Number: {bill_data['bill_number']}",
                 font=('Arial', 10)).pack(anchor=tk.W, pady=2)
        ttk.Label(left_info, text=f"Customer: {bill_data['customer_name']}",
                 font=('Arial', 10)).pack(anchor=tk.W, pady=2)

        # Show mobile number if available
        if bill_data.get('customer_mobile'):
            ttk.Label(left_info, text=f"Mobile: {bill_data['customer_mobile']}",
                     font=('Arial', 10)).pack(anchor=tk.W, pady=2)

        ttk.Label(left_info, text=f"Date: {bill_data['date']}",
                 font=('Arial', 10)).pack(anchor=tk.W, pady=2)
        ttk.Label(left_info, text=f"Time: {bill_data['time']}",
                 font=('Arial', 10)).pack(anchor=tk.W, pady=2)

        # Payment method information
        payment_method = bill_data.get('payment_method', 'Cash')
        payment_color = '#28a745' if payment_method == 'Cash' else '#007bff'  # Green for Cash, Blue for others
        ttk.Label(left_info, text=f"Payment Method: {payment_method}",
                 font=('Arial', 10, 'bold'), foreground=payment_color).pack(anchor=tk.W, pady=2)

        # Right side - Total amount
        right_info = ttk.Frame(info_frame)
        right_info.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(right_info, text="Total Amount",
                 font=('Arial', 12, 'bold')).pack(anchor=tk.E)
        ttk.Label(right_info, text=f"{self.currency}{bill_data['total_amount']:.2f}",
                 font=('Arial', 16, 'bold'),
                 foreground='#d63384').pack(anchor=tk.E, pady=10)

    def _create_order_details(self, main_frame, bill_data):
        """Create order details section"""
        order_frame = ttk.LabelFrame(main_frame, text="Order Details", padding="8")
        order_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 10))
        order_frame.columnconfigure(0, weight=1)
        order_frame.rowconfigure(0, weight=1)

        tree_frame = ttk.Frame(order_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ('category', 'item', 'qty', 'price', 'total')
        order_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        order_tree.heading('category', text='Category')
        order_tree.heading('item', text='Item')
        order_tree.heading('qty', text='Qty')
        order_tree.heading('price', text='Price')
        order_tree.heading('total', text='Total')

        order_tree.column('category', width=120)
        order_tree.column('item', width=250)
        order_tree.column('qty', width=50)
        order_tree.column('price', width=80)
        order_tree.column('total', width=80)

        order_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=order_tree.yview)
        order_tree.configure(yscrollcommand=order_scrollbar.set)

        order_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        order_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Add order items to treeview
        for item in bill_data['items']:
            order_tree.insert('', 'end', values=(
                item['category'],
                item['name'],
                item['quantity'],
                f"{self.currency}{item['price']:.2f}",
                f"{self.currency}{item['total']:.2f}"
            ))

    def _create_bill_summary(self, main_frame, bill_data):
        """Create bill summary section"""
        summary_frame = ttk.Frame(main_frame)
        summary_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        total_items = sum(item['quantity'] for item in bill_data['items'])
        unique_items = len(bill_data['items'])

        ttk.Label(summary_frame, text=f"Total Items: {total_items}",
                 font=('Arial', 10)).pack(side=tk.LEFT)
        ttk.Label(summary_frame, text=f"Unique Items: {unique_items}",
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=(20, 0))
        ttk.Label(summary_frame, text=f"Grand Total: {self.currency}{bill_data['total_amount']:.2f}",
                 font=('Arial', 12, 'bold'),
                 foreground='#d63384').pack(side=tk.RIGHT)

    def _create_action_buttons(self, main_frame, bill_data, bill_window):
        """Create action buttons section"""
        ttk.Separator(main_frame, orient='horizontal').grid(row=5, column=0, sticky=(tk.W, tk.E), pady=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        button_frame.columnconfigure(0, weight=1)

        print_frame = ttk.Frame(button_frame)
        print_frame.grid(row=0, column=0, sticky=tk.E, pady=5)

        ttk.Button(print_frame, text="Close",
                  command=bill_window.destroy,
                  style='Action.TButton').pack(side=tk.RIGHT, padx=(10, 0))

        ttk.Button(print_frame, text="🗑️ Delete Bill",
                  command=lambda: self._delete_bill_from_details(bill_data['bill_number'], bill_window),
                  style='Action.TButton').pack(side=tk.RIGHT, padx=(10, 0))

        ttk.Button(print_frame, text="📄 Print to Console",
                  command=lambda: self._print_bill_to_console(bill_data),
                  style='Action.TButton').pack(side=tk.RIGHT, padx=(10, 0))

        ttk.Button(print_frame, text="💾 Save as PDF",
                  command=lambda: self._save_bill_as_pdf_from_details(bill_data['bill_number']),
                  style='Action.TButton').pack(side=tk.RIGHT, padx=(10, 0))

        ttk.Button(print_frame, text="🖨️ Print Bill",
                  command=lambda: self._print_bill_from_details(bill_data['bill_number']),
                  style='Action.TButton').pack(side=tk.RIGHT, padx=(10, 0))

    # Helper methods for button actions
    def _print_bill_and_clear(self, bill_number, dialog, clear_callback):
        """Enhanced print bill method with better user feedback"""
        # Show progress message
        progress_dialog = tk.Toplevel(self.root)
        progress_dialog.title("Printing...")
        progress_dialog.geometry("400x150")
        progress_dialog.transient(dialog)
        progress_dialog.grab_set()

        # Center the progress dialog
        progress_dialog.update_idletasks()
        x = dialog.winfo_x() + (dialog.winfo_width() - 400) // 2
        y = dialog.winfo_y() + (dialog.winfo_height() - 150) // 2
        progress_dialog.geometry(f"400x150+{x}+{y}")

        progress_frame = ttk.Frame(progress_dialog, padding="20")
        progress_frame.pack(fill=tk.BOTH, expand=True)

        progress_label = ttk.Label(progress_frame, text="🖨️ Sending bill to Brother printer...",
                                 font=('Arial', 11))
        progress_label.pack(pady=10)

        progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        progress_bar.pack(fill=tk.X, pady=10)
        progress_bar.start()

        status_label = ttk.Label(progress_frame, text="Please wait...",
                               font=('Arial', 9), foreground='gray')
        status_label.pack()

        # Update the display
        progress_dialog.update()

        def do_print():
            """Perform the actual printing in a separate function"""
            try:
                # Update status
                status_label.config(text="Using enhanced notepad printing method...")
                progress_dialog.update()

                # Use the enhanced printing method
                success, file_path, message = self.billing_system.enhanced_print_bill_with_options(bill_number)

                # Stop progress bar
                progress_bar.stop()
                progress_dialog.destroy()

                # Show result
                if success:
                    messagebox.showinfo("Print Success", message)
                    if file_path:
                        # Ask if user wants to open the PDF
                        if messagebox.askyesno("PDF Backup",
                                             "A PDF backup was also created.\nWould you like to open it?"):
                            import os
                            os.startfile(file_path)
                else:
                    messagebox.showerror("Print Error", message)

            except Exception as e:
                progress_bar.stop()
                progress_dialog.destroy()
                messagebox.showerror("Print Error", f"An error occurred while printing:\n{str(e)}")

        # Schedule the printing after a short delay to show the progress dialog
        self.root.after(500, do_print)

        # Clear order and close after printing
        self._clear_order_and_close(dialog, clear_callback)

    def _save_pdf_and_clear(self, bill_number, dialog, clear_callback):
        file_path = self.billing_system.save_bill_as_pdf(bill_number)
        if file_path:
            messagebox.showinfo("PDF Saved", f"Bill saved as PDF:\n{file_path}")
        else:
            messagebox.showerror("Save Error", "Failed to save bill as PDF")
        self._clear_order_and_close(dialog, clear_callback)

    def _view_bill_and_clear(self, bill_number, dialog, clear_callback):
        bill_data = self.billing_system.get_bill_details_for_display(bill_number)
        if bill_data:
            self.show_bill_details_window(bill_data)
        self._clear_order_and_close(dialog, clear_callback)

    def _clear_order_and_close(self, dialog, clear_callback):
        clear_callback()
        dialog.destroy()

    def _print_bill_from_details(self, bill_number):
        success, file_path, message = self.billing_system.print_or_save_bill(bill_number)
        if success:
            messagebox.showinfo("Print Result", message)
        else:
            messagebox.showerror("Print Error", message)

    def _save_bill_as_pdf_from_details(self, bill_number):
        file_path = self.billing_system.save_bill_as_pdf(bill_number)
        if file_path:
            messagebox.showinfo("PDF Saved", f"Bill saved as PDF:\n{file_path}")
        else:
            messagebox.showerror("Save Error", "Failed to save bill as PDF")

    def _print_bill_to_console(self, bill_data):
        bill_items = []
        for item in bill_data['items']:
            bill_items.append({
                'name': item['name'],
                'quantity': item['quantity'],
                'price': item['price'],
                'total': item['total']
            })

        self.billing_system.print_bill(
            bill_data['bill_number'],
            bill_data['customer_name'],
            bill_data.get('customer_mobile', ''),
            bill_items,
            bill_data['total_amount'],
            bill_data['date'],
            bill_data['time']
        )
        messagebox.showinfo("Success", "Bill printed to console/terminal")

    def _delete_bill_from_details(self, bill_number, bill_window):
        confirm_result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete bill {bill_number}?\n\n"
            f"This action cannot be undone and will permanently remove:\n"
            f"• The bill record\n"
            f"• All associated order items\n"
            f"• Any saved PDF files will remain but the database record will be gone\n\n"
            f"Do you want to proceed?",
            icon='warning'
        )

        if confirm_result:
            success = self.billing_system.delete_bill(bill_number)
            if success:
                messagebox.showinfo("Success", f"Bill {bill_number} has been deleted successfully!")
                bill_window.destroy()
            else:
                messagebox.showerror("Error", f"Failed to delete bill {bill_number}. Please try again.")

    def search_bill(self):
        """Search for a bill by number"""
        bill_number = simpledialog.askstring("Search Bill", "Enter Bill Number:")
        if bill_number:
            bill_data = self.billing_system.get_bill_details_for_display(bill_number.strip().upper())
            if bill_data:
                self.show_bill_details_window(bill_data)
            else:
                messagebox.showinfo("Not Found", "Bill not found")
