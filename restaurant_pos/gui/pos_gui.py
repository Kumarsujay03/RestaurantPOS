"""
Optimized Restaurant POS GUI - Main Interface
Uses modular components for better organization and maintainability
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Import our modular components
from restaurant_pos.core.food_manager import FoodItemManager
from restaurant_pos.core.billing_system import BillingSystem
from restaurant_pos.core.database import DatabaseManager
from restaurant_pos.core.config import get_restaurant_name, get_currency_symbol
from restaurant_pos.gui.management_gui import ManagementInterface

# Import our new modular GUI components
from restaurant_pos.gui.gui_components import StyleManager, TimeDisplay
from restaurant_pos.gui.menu_display import MenuDisplay
from restaurant_pos.gui.order_manager import OrderManager
from restaurant_pos.gui.bill_dialogs import BillDialogs
from restaurant_pos.gui.bill_reports import BillReports


class RestaurantPOS:
    """Main Restaurant POS Application - Now Modular and Optimized"""

    def __init__(self, root):
        self.root = root
        self._initialize_application()
        self._setup_managers()
        self._create_main_interface()
        self._load_initial_data()

    def _initialize_application(self):
        """Initialize basic application settings"""
        restaurant_name = get_restaurant_name()
        self.root.title(f"{restaurant_name} - Point of Sale System")

        # Set window to full screen by default - improved implementation
        self.root.state('zoomed')  # Windows maximized mode first
        self.root.update_idletasks()  # Process pending events
        self.root.attributes('-fullscreen', True)  # Then true full screen mode
        self.root.configure(bg='#f0f0f0')
        self.root.resizable(True, True)

        # Bind keys for full screen control
        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('<Escape>', self.exit_fullscreen)

        # Initialize fullscreen state
        self.fullscreen_state = True

    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode on F11 key press"""
        self.fullscreen_state = not self.fullscreen_state  # Toggle state
        self.root.attributes('-fullscreen', self.fullscreen_state)

    def exit_fullscreen(self, event=None):
        """Exit fullscreen mode on Escape key press"""
        self.fullscreen_state = False
        self.root.attributes('-fullscreen', False)
        self.root.state('normal')  # Restore to windowed mode

    def _setup_managers(self):
        """Initialize all manager classes"""
        # Get currency symbol
        self.currency = get_currency_symbol()

        # Core system managers
        self.food_manager = FoodItemManager()
        self.billing_system = BillingSystem()
        self.management_interface = ManagementInterface(self.root, self.food_manager)

        # GUI component managers
        self.order_manager = OrderManager(self.root, self.currency)
        self.bill_dialogs = BillDialogs(self.root, self.billing_system, self.currency)
        self.bill_reports = BillReports(
            self.root,
            self.billing_system,
            self.currency,
            self.bill_dialogs.show_bill_details_window
        )

    def _create_main_interface(self):
        """Create the main POS interface with adjustable panel widths using PanedWindow"""
        # Setup styles
        StyleManager.setup_styles()

        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)  # Main content area should expand
        main_frame.rowconfigure(2, weight=0)  # Footer should not expand
        main_frame.columnconfigure(0, weight=1)

        self._create_header(main_frame)
        self._create_adjustable_panels(main_frame)
        self._create_footer(main_frame)

    def _create_adjustable_panels(self, main_frame):
        """Create adjustable panels using PanedWindow for manual width control"""
        # Create main paned window for horizontal adjustment
        self.main_paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        self.main_paned.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))  # No bottom padding

        # Left panel - Menu (adjustable width)
        left_frame = ttk.LabelFrame(self.main_paned, text="Menu", padding="10")
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)

        # Middle paned window for order and actions
        self.middle_paned = ttk.PanedWindow(self.main_paned, orient=tk.HORIZONTAL)

        # Middle panel - Current Order (adjustable width)
        middle_frame = ttk.LabelFrame(self.middle_paned, text="Current Order", padding="10")
        middle_frame.columnconfigure(0, weight=1)
        middle_frame.rowconfigure(1, weight=1)

        # Right panel - Actions (adjustable width) - extend to full height
        right_frame = ttk.LabelFrame(self.middle_paned, text="Actions", padding="3")
        right_frame.columnconfigure(0, weight=1)
        # Configure rows to allow proper expansion
        right_frame.rowconfigure(0, weight=0)  # Billing section - fixed size
        right_frame.rowconfigure(1, weight=0)  # Management section - fixed size
        right_frame.rowconfigure(2, weight=1)  # Quick actions section - expandable

        # Add panels to paned windows
        self.main_paned.add(left_frame, weight=3)  # Initial weight for menu
        self.main_paned.add(self.middle_paned, weight=7)  # Combined weight for order+actions

        self.middle_paned.add(middle_frame, weight=2)  # Further reduced weight for order
        self.middle_paned.add(right_frame, weight=5)   # Further increased weight for actions

        # Set minimum sizes for panels
        left_frame.config(width=300)    # Minimum width for menu
        middle_frame.config(width=350)  # Reduced minimum width for order
        right_frame.config(width=250, height=700)   # Increased minimum width and height for actions

        # Initialize panel contents
        self._setup_menu_panel(left_frame)
        self._setup_order_panel(middle_frame)
        self._setup_actions_panel(right_frame)

    def _setup_menu_panel(self, left_frame):
        """Setup the menu panel content"""
        # Initialize menu display with callback to order manager
        self.menu_display = MenuDisplay(
            left_frame,
            self.food_manager,
            self.order_manager.add_item_to_order
        )
        self.menu_display.setup_menu_display(left_frame)

    def _setup_order_panel(self, middle_frame):
        """Setup the current order panel content"""
        self.order_manager.setup_order_display(middle_frame)

    def _setup_actions_panel(self, right_frame):
        """Setup the actions panel content"""
        # Create action sections with compact layout
        self._create_compact_actions(right_frame)

    def _create_compact_actions(self, right_frame):
        """Create compact action panel with minimal white space and full button visibility"""
        # Create billing actions with reduced padding
        billing_frame = ttk.LabelFrame(right_frame, text="💳 Billing", padding="5")
        billing_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        billing_frame.columnconfigure(0, weight=1)

        # Compact button layout
        button_padding = 2  # Minimal padding

        billing_buttons = [
            ("💳 Generate Bill", self.generate_bill),
            ("🔍 Search Bill", self.bill_dialogs.search_bill),
            ("📅 Bills by Date", self.bill_reports.bills_by_date),
            ("📊 Sales Summary", self.bill_reports.sales_summary)
        ]

        for i, (text, command) in enumerate(billing_buttons):
            btn = ttk.Button(billing_frame, text=text, command=command, style='Action.TButton')
            btn.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=button_padding)

        # Management actions with compact layout
        menu_frame = ttk.LabelFrame(right_frame, text="🏪 Management", padding="5")
        menu_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        menu_frame.columnconfigure(0, weight=1)

        management_buttons = [
            ("🏪 Restaurant Mgmt", self.show_management_interface),
            ("💰 Manage Expenses", self.show_expense_management),
            ("🔄 Refresh Menu", self.load_menu_items)
        ]

        for i, (text, command) in enumerate(management_buttons):
            btn = ttk.Button(menu_frame, text=text, command=command, style='Action.TButton')
            btn.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=button_padding)

        # Quick actions with enhanced layout to ensure all buttons are visible
        quick_frame = ttk.LabelFrame(right_frame, text="🚀 Quick Actions", padding="5")
        quick_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        quick_frame.columnconfigure(0, weight=1)

        # Configure all rows to be visible without scrolling
        for i in range(10):  # Give enough rows
            quick_frame.rowconfigure(i, weight=0)

        quick_buttons = [
            ("📋 View All Bills", self.bill_reports.view_all_bills),
            ("🍽️ View Full Menu", lambda: self.bill_reports.view_full_menu(self.food_manager))
        ]

        # Create buttons with proper spacing
        for i, (text, command) in enumerate(quick_buttons):
            btn = ttk.Button(quick_frame, text=text, command=command, style='Action.TButton')
            btn.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=button_padding, ipady=3)

        # Add a small expandable spacer at the bottom
        spacer_frame = ttk.Frame(quick_frame)
        spacer_frame.grid(row=len(quick_buttons), column=0, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        quick_frame.rowconfigure(len(quick_buttons), weight=1)  # Only the spacer should expand

    def _create_footer(self, main_frame):
        """Create footer section with close button - minimal height"""
        # Add a very thin separator line for visual separation
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(2, 1))

        # Footer frame with minimal padding - reduced height
        footer_frame = ttk.Frame(main_frame, padding="2")
        footer_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 1))
        footer_frame.columnconfigure(0, weight=1)  # Left side expands
        footer_frame.columnconfigure(1, weight=0)  # Right side (button) stays fixed

        # Application info on the left - much smaller font and minimal padding
        info_label = ttk.Label(footer_frame,
                              text="POS System Ready | F11: Full-Screen | ESC: Exit | Drag borders to resize panels",
                              font=('Arial', 7),  # Even smaller font
                              foreground='#999999')
        info_label.grid(row=0, column=0, sticky=tk.W)

        # Close button on the right - smaller button
        close_button = ttk.Button(footer_frame,
                                 text="✕ Exit",  # Shorter text
                                 command=self._safe_close_application,
                                 style='Action.TButton')
        close_button.grid(row=0, column=1, sticky=tk.E, padx=(3, 0))

    def _create_header(self, main_frame):
        """Create header section"""
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)  # Make middle section expandable

        # Left side - Restaurant name
        restaurant_name = get_restaurant_name()
        ttk.Label(header_frame, text=f"🍽️ {restaurant_name} - POS System",
                  style='Title.TLabel').grid(row=0, column=0, sticky=tk.W)

        # Middle section - Printer status
        self.printer_status_frame = ttk.Frame(header_frame)
        self.printer_status_frame.grid(row=0, column=1, padx=20)

        # Create printer status display
        self._create_printer_status_display()

        # Right side - Current time with time display manager
        time_label = ttk.Label(header_frame, text="", style='Header.TLabel')
        time_label.grid(row=0, column=2, sticky=tk.E)
        self.time_display = TimeDisplay(time_label)

    def _create_printer_status_display(self):
        """Create the printer status display in the header"""
        # Create a frame for the printer status with better styling
        status_container = ttk.Frame(self.printer_status_frame)
        status_container.pack()

        # Printer icon
        self.printer_icon = ttk.Label(status_container, text="🖨️", font=('Arial', 12))
        self.printer_icon.pack(side=tk.LEFT, padx=(0, 5))

        # Printer status text
        self.printer_status_label = ttk.Label(status_container, text="Checking printer...",
                                            style='Header.TLabel', font=('Arial', 10))
        self.printer_status_label.pack(side=tk.LEFT)

        # Add clickable status for refresh
        self.printer_refresh_btn = ttk.Button(status_container, text="🔄", width=3,
                                            command=self._refresh_printer_status)
        self.printer_refresh_btn.pack(side=tk.LEFT, padx=(5, 0))

        # Check printer status initially and set up periodic checking
        self._check_printer_status()
        self._setup_printer_status_monitoring()

    def _check_printer_status(self):
        """Check current printer status and update display"""
        try:
            # Get printer status from billing system
            printer = self.billing_system.printer

            if printer.is_physical_printer_available():
                printers = printer.get_available_printers()
                if printers:
                    # Find Brother printer specifically
                    brother_printer = None
                    for p in printers:
                        if 'brother' in p['name'].lower():
                            brother_printer = p
                            break

                    if brother_printer:
                        # Brother printer found and online
                        status_text = f"Brother Printer: Online"
                        if brother_printer.get('default'):
                            status_text += " (Default)"

                        self.printer_status_label.config(text=status_text, foreground='green')
                        self.printer_icon.config(text="🖨️", foreground='green')

                        # Add tooltip with printer name
                        self._create_tooltip(self.printer_status_label,
                                           f"Printer: {brother_printer['name']}\nStatus: Online and Ready")
                    else:
                        # Other printer found but not Brother
                        default_printer = next((p for p in printers if p.get('default')), printers[0])
                        self.printer_status_label.config(text=f"Printer: {default_printer['name'][:15]}...",
                                                       foreground='orange')
                        self.printer_icon.config(text="🖨️", foreground='orange')
                else:
                    # No printers detected
                    self.printer_status_label.config(text="No Printer Connected", foreground='red')
                    self.printer_icon.config(text="⚠️", foreground='red')
            else:
                # No physical printer available
                self.printer_status_label.config(text="No Physical Printer", foreground='red')
                self.printer_icon.config(text="❌", foreground='red')

        except Exception as e:
            # Error checking printer
            self.printer_status_label.config(text="Printer Check Failed", foreground='red')
            self.printer_icon.config(text="❌", foreground='red')
            print(f"Printer status check error: {e}")

    def _refresh_printer_status(self):
        """Manually refresh printer status with improved feedback"""
        self.printer_status_label.config(text="Refreshing...", foreground='gray')
        self.printer_icon.config(text="🔄", foreground='gray')

        # Force refresh of printer list in billing system
        try:
            self.billing_system.printer.refresh_printer_list()
        except:
            pass

        # Small delay to show the refresh action
        self.root.after(1000, self._check_printer_status)

    def _setup_printer_status_monitoring(self):
        """Set up periodic printer status monitoring"""
        # Check printer status every 30 seconds
        def periodic_check():
            self._check_printer_status()
            self.root.after(30000, periodic_check)  # 30 seconds

        # Start periodic checking after initial load
        self.root.after(5000, periodic_check)  # First check after 5 seconds

    def _create_tooltip(self, widget, text):
        """Create a simple tooltip for the widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")

            tooltip_label = ttk.Label(tooltip, text=text,
                                    background='lightyellow',
                                    relief='solid', borderwidth=1,
                                    font=('Arial', 9))
            tooltip_label.pack()

            widget.tooltip = tooltip

        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip

        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)

    def _load_initial_data(self):
        """Load initial application data"""
        self.load_menu_items()

        # Ensure printer status is checked after GUI is fully loaded
        self.root.after(2000, self._initial_printer_check)

    def _initial_printer_check(self):
        """Perform initial printer check after GUI is fully loaded"""
        print("🔍 Performing initial printer detection for GUI...")

        # Add extra delay for IDE environments
        import sys
        if not hasattr(sys, 'ps1') and 'PYTHONPATH' in os.environ:
            print("🔧 IDE environment detected, adding extra initialization time...")
            # Wait a bit more for IDE environments
            self.root.after(1000, self._delayed_printer_check)
        else:
            self._delayed_printer_check()

    def _delayed_printer_check(self):
        """Delayed printer check with enhanced error handling"""
        try:
            print("🖨️ Starting enhanced printer detection...")

            # Force refresh the printer list to ensure latest status
            self.billing_system.printer.refresh_printer_list()
            print("✅ Printer list refreshed successfully")

            # Try multiple detection methods
            self._try_multiple_printer_detection()

        except Exception as e:
            print(f"⚠️ Error in delayed printer check: {e}")
            # Fallback: try basic detection
            self._fallback_printer_detection()

    def _try_multiple_printer_detection(self):
        """Try multiple methods to detect printers"""
        printer_found = False

        # Method 1: Use our enhanced printer system
        try:
            if self.billing_system.printer.is_physical_printer_available():
                printers = self.billing_system.printer.get_available_printers()
                if printers:
                    printer_found = True
                    print(f"✅ Method 1: Found {len(printers)} printer(s) via enhanced system")
        except Exception as e:
            print(f"❌ Method 1 failed: {e}")

        # Method 2: Direct win32print check (for IDE environments)
        if not printer_found:
            try:
                import win32print
                printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
                if printers:
                    print(f"✅ Method 2: Found {len(printers)} printer(s) via direct win32print")
                    # Update our printer system with this info
                    self._update_printer_status_from_direct_check(printers)
                    printer_found = True
            except Exception as e:
                print(f"❌ Method 2 failed: {e}")

        # Update the GUI display
        self._check_printer_status()

        # Print final status
        if printer_found:
            printers = self.billing_system.printer.get_available_printers()
            print(f"🖨️ Final result: {len(printers)} physical printer(s) detected:")
            for printer in printers:
                print(f"   - {printer['name']} ({'Online' if printer['online'] else 'Offline'})")
        else:
            print("❌ Final result: No physical printers detected")
            self._show_printer_troubleshooting()

    def _update_printer_status_from_direct_check(self, win32_printers):
        """Update printer status from direct win32print check"""
        try:
            # Clear existing printers and add detected ones
            self.billing_system.printer.physical_printers = []

            for printer in win32_printers:
                printer_name = printer[2]
                # Filter out virtual printers
                if not any(virtual in printer_name.lower() for virtual in
                          ['pdf', 'xps', 'fax', 'onenote', 'virtual', 'microsoft']):
                    printer_info = {
                        'name': printer_name,
                        'status': 'Available',
                        'online': True,
                        'default': False
                    }
                    self.billing_system.printer.physical_printers.append(printer_info)
                    print(f"✅ Added printer: {printer_name}")

            # Set default printer
            if self.billing_system.printer.physical_printers:
                try:
                    import win32print
                    default_name = win32print.GetDefaultPrinter()
                    for printer in self.billing_system.printer.physical_printers:
                        if printer['name'] == default_name:
                            printer['default'] = True
                            self.billing_system.printer.default_printer = printer
                            break
                except:
                    # If can't get default, use first one
                    self.billing_system.printer.physical_printers[0]['default'] = True
                    self.billing_system.printer.default_printer = self.billing_system.printer.physical_printers[0]

        except Exception as e:
            print(f"❌ Error updating printer status: {e}")

    def _fallback_printer_detection(self):
        """Fallback printer detection method"""
        print("🔄 Using fallback printer detection...")
        try:
            # Simple check - just try to get default printer
            import win32print
            default_printer = win32print.GetDefaultPrinter()
            if default_printer:
                print(f"✅ Fallback: Found default printer: {default_printer}")
                # Manually set this in our system
                self.billing_system.printer.physical_printers = [{
                    'name': default_printer,
                    'status': 'Available',
                    'online': True,
                    'default': True
                }]
                self.billing_system.printer.default_printer = self.billing_system.printer.physical_printers[0]
        except Exception as e:
            print(f"❌ Fallback detection failed: {e}")

        # Update GUI regardless
        self._check_printer_status()

    def _show_printer_troubleshooting(self):
        """Show printer troubleshooting info in console"""
        print("\n🔧 PRINTER TROUBLESHOOTING:")
        print("1. Ensure printer is powered on and connected")
        print("2. Check if printer drivers are installed")
        print("3. Try setting printer as default in Windows Settings")
        print("4. If using IDE, try running from terminal: python run_pos.py")
        print("5. Check Windows Print Spooler service is running")
        print("6. Click the 🔄 refresh button in the GUI header")
        print("=" * 50)

    # Core business logic methods
    def generate_bill(self):
        """Generate bill for current order with payment method tracking"""
        if not self.order_manager.has_items():
            messagebox.showwarning("Warning", "No items in order")
            return

        # Use the new validation method from order manager
        if not self.order_manager.validate_customer_info():
            return  # Validation failed, error message already shown

        customer_info = self.order_manager.get_customer_info()

        # Get order items and create bill with payment method
        order_items = self.order_manager.get_order_items()
        bill_number = self.billing_system.create_bill(
            customer_info['name'],
            customer_info['mobile'],
            order_items,
            auto_print=False,
            payment_method=customer_info['payment_method']  # NEW: Pass payment method
        )

        if bill_number:
            # Show bill success dialog with clear order callback
            self.bill_dialogs.show_bill_success_dialog(
                bill_number,
                self._clear_order_callback
            )
        else:
            messagebox.showerror("Error", "Failed to generate bill")

    def load_menu_items(self):
        """Load menu items using menu display manager"""
        self.menu_display.load_menu_items()

    def show_management_interface(self):
        """Show the comprehensive management interface"""
        self.management_interface.show_management_window()
        # Refresh the menu after management operations
        self.load_menu_items()

    def show_expense_management(self):
        """Show the expense management interface"""
        from restaurant_pos.gui.expense_manager import ExpenseManager
        expense_manager = ExpenseManager(self.root)
        expense_manager.show_expense_window()

    def _clear_order_callback(self):
        """Callback function to clear order (used by bill dialogs)"""
        self.order_manager.clear_order()

    def _safe_close_application(self):
        """Safely close the application with confirmation if there are unsaved orders"""
        # Check if there are items in current order
        if self.order_manager.has_items():
            result = messagebox.askyesnocancel(
                "Confirm Exit",
                "There are items in the current order.\n\n"
                "Do you want to generate a bill before closing?\n\n"
                "• Yes: Generate bill first\n"
                "• No: Close without saving\n"
                "• Cancel: Return to application"
            )

            if result is None:  # Cancel
                return
            elif result:  # Yes - generate bill first
                if self.order_manager.validate_customer_info():
                    # Try to generate bill
                    customer_info = self.order_manager.get_customer_info()
                    order_items = self.order_manager.get_order_items()
                    bill_number = self.billing_system.create_bill(
                        customer_info['name'],
                        customer_info['mobile'],
                        order_items,
                        auto_print=False
                    )
                    if bill_number:
                        messagebox.showinfo("Success", f"Bill {bill_number} generated successfully!")
                else:
                    return  # Validation failed, don't close
            # If No or successful bill generation, proceed to close

        # Close the application
        self.root.quit()
def main():
    """Main application entry point"""
    root = tk.Tk()
    app = RestaurantPOS(root)
    root.mainloop()


if __name__ == "__main__":
    main()
