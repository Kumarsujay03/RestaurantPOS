"""
Menu Display Module
Handles all menu-related display functionality
"""
import tkinter as tk
from tkinter import ttk
from restaurant_pos.gui.gui_components import TooltipManager

class MenuDisplay:
    """Handles menu categories and items display"""

    def __init__(self, parent, food_manager, add_item_callback):
        self.parent = parent
        self.food_manager = food_manager
        self.add_item_callback = add_item_callback
        self.categories_frame = None
        self.items_scrollable_frame = None
        self.items_canvas = None

    def setup_menu_display(self, left_frame):
        """Setup the complete menu display area with simple, direct layout"""
        # Categories section
        cat_frame = ttk.Frame(left_frame)
        cat_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(cat_frame, text="Menu Categories", style='Header.TLabel', font=('Arial', 12, 'bold')).pack(anchor=tk.W)

        self.categories_frame = ttk.Frame(cat_frame)
        self.categories_frame.pack(fill=tk.X, pady=(5, 0))

        # Items display section - optimized frame with scrollbar for better space utilization
        items_frame = ttk.LabelFrame(left_frame, text="Menu Items", padding="3")
        items_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        items_frame.columnconfigure(0, weight=1)
        items_frame.rowconfigure(0, weight=1)

        # Create a canvas with optimized configuration for better space utilization
        self.items_canvas = tk.Canvas(items_frame, bg='#f8f9fa', highlightthickness=0, width=400)
        items_scrollbar = ttk.Scrollbar(items_frame, orient="vertical", command=self.items_canvas.yview)
        self.items_scrollable_frame = ttk.Frame(self.items_canvas)

        # Configure canvas scrolling
        self.items_canvas.configure(yscrollcommand=items_scrollbar.set)

        # Create window in canvas and bind configure event with optimized width utilization
        canvas_window = self.items_canvas.create_window((0, 0), window=self.items_scrollable_frame, anchor="nw")

        def configure_scroll_region(event):
            self.items_canvas.configure(scrollregion=self.items_canvas.bbox("all"))
            # Maximize space utilization - use full canvas width with minimal margin
            canvas_width = self.items_canvas.winfo_width()
            if canvas_width > 1:  # Only update if canvas has been drawn
                # Use full width with just 1 pixel margin for optimal space utilization
                self.items_canvas.itemconfig(canvas_window, width=canvas_width-1)

        self.items_scrollable_frame.bind("<Configure>", configure_scroll_region)
        self.items_canvas.bind("<Configure>", configure_scroll_region)

        # Grid the canvas and scrollbar with optimized spacing
        self.items_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 0))
        items_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S), padx=(1, 0))

        # Enhanced mouse wheel scrolling - bind to all menu components
        self._setup_enhanced_scrolling(left_frame, items_frame, self.items_canvas, self.items_scrollable_frame)

        # Add status label for menu feedback
        self.menu_status_label = ttk.Label(items_frame, text="Loading menu...",
                                         font=('Arial', 9), foreground='#666666')
        self.menu_status_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))

    def load_menu_items(self):
        """Load menu categories and items with responsive design optimized for 1024x768"""
        # Clear existing widgets
        for widget in self.categories_frame.winfo_children():
            widget.destroy()

        categories = self.food_manager.get_categories()

        if not categories:
            ttk.Label(self.categories_frame, text="No categories available").pack()
            return

        # Better column calculation to ensure buttons stay within screen bounds
        total_categories = len(categories)

        # Better column calculation for better visibility and fit within bounds
        if total_categories <= 3:
            columns = total_categories
        elif total_categories <= 6:
            columns = 3
        else:
            columns = 3  # Use only 3 columns max to prevent buttons going out of screen

        # Create category buttons that fit their content with proper grid spacing
        for i, category in enumerate(categories):
            # Shorter text to ensure buttons fit within available space
            display_text = category if len(category) <= 10 else category[:8] + ".."

            btn = ttk.Button(self.categories_frame, text=display_text,
                           command=lambda c=category: self.show_category_items(c),
                           style='Category.TButton')

            row = i // columns
            col = i % columns
            btn.grid(row=row, column=col, padx=2, pady=2, sticky=(tk.W, tk.E))

        # Configure grid weights for responsive behavior with proper width constraints
        for i in range(columns):
            self.categories_frame.columnconfigure(i, weight=1, minsize=70, uniform="category")

        # Update status
        self.menu_status_label.config(text=f"Loaded {total_categories} categories")

        # Show all items initially
        self.show_all_items()

    def show_all_items(self):
        """Show all menu items with responsive grid layout"""
        # Clear existing items
        for widget in self.items_scrollable_frame.winfo_children():
            widget.destroy()

        # Reset canvas scroll position to top when showing all items
        self.items_canvas.yview_moveto(0)

        # Get all items from the food manager
        all_items = self.food_manager.get_all_items()

        if not all_items:
            # Show message if no items available
            ttk.Label(self.items_scrollable_frame, text="No menu items available",
                     font=('Arial', 12, 'italic')).pack(pady=20)
            self.menu_status_label.config(text="No items to display")
            # Update scroll region for empty state
            self._update_scroll_region()
            return

        # Update status
        self.menu_status_label.config(text=f"Displaying {len(all_items)} items")

        # Group items by category for better organization
        items_by_category = {}
        for item in all_items:
            category = item['category']
            if category not in items_by_category:
                items_by_category[category] = []
            items_by_category[category].append(item)

        row = 0
        for category, items in items_by_category.items():
            # Simple category header without show only button
            category_label = ttk.Label(self.items_scrollable_frame, text=f"📂 {category}",
                                     font=('Arial', 11, 'bold'))
            category_label.grid(row=row, column=0, sticky=tk.W, pady=(10, 5))
            row += 1

            # Items in this category with responsive grid
            self._create_responsive_item_grid(items, row)
            row += len(items)  # Update row based on number of items

        # Properly update canvas scroll region after adding new content
        self._update_scroll_region()

    def show_category_items(self, category):
        """Show items for a specific category with responsive layout"""
        # Clear existing items
        for widget in self.items_scrollable_frame.winfo_children():
            widget.destroy()

        # Reset canvas scroll position to top when showing new category
        self.items_canvas.yview_moveto(0)

        # Get items for the specific category
        items = self.food_manager.get_items_by_category(category)

        if not items:
            # Show message if no items in this category
            no_items_frame = ttk.Frame(self.items_scrollable_frame)
            no_items_frame.pack(pady=20, fill='x')

            ttk.Label(no_items_frame, text=f"No items in category '{category}'",
                     font=('Arial', 12, 'italic')).pack()

            ttk.Button(no_items_frame, text="Show All Categories",
                      command=self.show_all_items,
                      style='Category.TButton').pack(pady=10)

            self.menu_status_label.config(text=f"No items in {category}")
            # Update scroll region for empty category
            self._update_scroll_region()
            return

        # Category header with back button
        header_frame = ttk.Frame(self.items_scrollable_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)

        ttk.Button(header_frame, text="← All Categories",
                  command=self.show_all_items,
                  style='Category.TButton').grid(row=0, column=0, sticky=tk.W)

        ttk.Label(header_frame, text=f"📂 {category} ({len(items)} items)",
                 font=('Arial', 12, 'bold')).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        self.menu_status_label.config(text=f"Showing {len(items)} items from {category}")

        # Items in this category with responsive grid - use smaller buttons for individual categories
        self._create_responsive_item_grid(items, 1, use_small_buttons=True)

        # Properly update canvas scroll region after adding new content
        self._update_scroll_region()

    def _create_responsive_item_grid(self, items, start_row, use_small_buttons=False):
        """Create responsive grid layout for menu items with multiple columns"""
        # Use 2 columns instead of 3 to ensure all buttons are visible
        columns = 2

        for i, item in enumerate(items):
            row = start_row + (i // columns)
            col = i % columns
            self._create_item_button(item, row, col, use_small_buttons)

    def _create_item_button(self, item, row, col, use_small_buttons=False):
        """Create item buttons that show full names without truncation and maximize space usage"""
        # Simple item name only - no price on button
        item_name = item['name']
        # Show full name without truncation - let wraplength handle the display
        display_name = item_name

        # Set button text and style based on availability and view type
        if item['available']:
            item_text = display_name
            btn_style = 'ItemSmall.TButton' if use_small_buttons else 'Item.TButton'
            state = 'normal'
        else:
            item_text = f"{display_name} (Out)"
            btn_style = 'ItemSmall.TButton' if use_small_buttons else 'Item.TButton'
            state = 'disabled'

        # Create button that shows full item name with optimized spacing
        item_btn = ttk.Button(self.items_scrollable_frame, text=item_text,
                            command=lambda i=item: self.add_item_callback(i),
                            style=btn_style, state=state)
        # Reduce padding between buttons to maximize space utilization
        item_btn.grid(row=row, column=col, padx=1, pady=1, sticky=(tk.W, tk.E), ipadx=2)

        # Configure column weights to ensure buttons expand properly within available space
        self.items_scrollable_frame.columnconfigure(col, weight=1, minsize=50)

        # Add enhanced scroll support to button
        self._bind_scroll_events(item_btn)

        # Create comprehensive tooltip with price information
        tooltip_text = f"Item: {item['name']}\nCategory: {item['category']}\nPrice: ₹{item['price']:.2f}"
        if not item['available']:
            tooltip_text += "\nStatus: Out of Stock"
        else:
            tooltip_text += "\nClick to add to order"

        TooltipManager.create_tooltip(item_btn, tooltip_text)

    def _bind_scroll_events(self, widget):
        """Bind comprehensive scroll events for touchpad and mouse wheel support"""
        # Windows and Linux mouse wheel events
        widget.bind("<MouseWheel>", self._on_mousewheel)

        # Linux specific scroll events
        widget.bind("<Button-4>", self._on_mousewheel)
        widget.bind("<Button-5>", self._on_mousewheel)

        # Touchpad specific events (for better laptop support)
        widget.bind("<Shift-MouseWheel>", self._on_horizontal_scroll)

        # Bind to all child widgets recursively for better touchpad support
        def bind_to_children(parent_widget):
            for child in parent_widget.winfo_children():
                try:
                    child.bind("<MouseWheel>", self._on_mousewheel)
                    child.bind("<Button-4>", self._on_mousewheel)
                    child.bind("<Button-5>", self._on_mousewheel)
                    bind_to_children(child)
                except:
                    pass

        widget.after(100, lambda: bind_to_children(widget))

    def _on_mousewheel(self, event):
        """Enhanced mouse wheel and touchpad scroll handling"""
        try:
            # Determine scroll direction and amount
            if event.delta:
                # Windows
                delta = -1 * (event.delta / 120)
            elif event.num == 4:
                # Linux scroll up
                delta = -1
            elif event.num == 5:
                # Linux scroll down
                delta = 1
            else:
                return

            # Smooth scrolling with variable speed
            scroll_amount = int(delta * 3)  # Adjust scroll sensitivity
            self.items_canvas.yview_scroll(scroll_amount, "units")
        except:
            pass

        return "break"  # Prevent event propagation

    def _on_horizontal_scroll(self, event):
        """Handle horizontal scrolling for touchpads"""
        try:
            if event.delta:
                delta = -1 * (event.delta / 120)
                self.items_canvas.xview_scroll(int(delta * 2), "units")
        except:
            pass
        return "break"

    def _on_touchpad_scroll(self, event):
        """Handle touchpad scrolling motion"""
        if hasattr(event, 'y_root') and hasattr(self, '_last_touchpad_y'):
            delta_y = event.y_root - self._last_touchpad_y
            if abs(delta_y) > 5:  # Minimum threshold for scroll
                direction = 1 if delta_y > 0 else -1
                self.items_canvas.yview_scroll(direction, "units")
        self._last_touchpad_y = getattr(event, 'y_root', 0)

    def _update_scroll_region(self):
        """Update canvas scroll region with proper timing and bounds checking"""
        def update_region():
            try:
                # Force update of all widget geometry
                self.items_scrollable_frame.update_idletasks()
                self.items_canvas.update_idletasks()

                # Wait a bit more for all widgets to be properly positioned
                self.items_canvas.after(10, lambda: self._finalize_scroll_region())

            except Exception as e:
                # Fallback in case of any issues
                self._finalize_scroll_region()

        # Schedule the update to happen after the current event processing
        self.items_canvas.after_idle(update_region)

    def _finalize_scroll_region(self):
        """Finalize the scroll region calculation after all widgets are positioned"""
        try:
            # Force final geometry update
            self.items_scrollable_frame.update_idletasks()

            # Calculate actual content height based on widgets
            max_y = 0
            for widget in self.items_scrollable_frame.winfo_children():
                try:
                    widget_y = widget.winfo_y() + widget.winfo_height()
                    max_y = max(max_y, widget_y)
                except:
                    continue

            # Add some padding and ensure minimum height
            content_height = max(max_y + 20, 100)
            canvas_width = self.items_canvas.winfo_width()

            # Set scroll region to exact content bounds
            self.items_canvas.configure(scrollregion=(0, 0, canvas_width, content_height))

            # Reset to top
            self.items_canvas.yview_moveto(0)

        except Exception as e:
            # Ultimate fallback - use bbox if available
            try:
                bbox = self.items_canvas.bbox("all")
                if bbox:
                    self.items_canvas.configure(scrollregion=bbox)
                else:
                    self.items_canvas.configure(scrollregion=(0, 0, 0, 0))
                self.items_canvas.yview_moveto(0)
            except:
                pass

    def _setup_enhanced_scrolling(self, left_frame, items_frame, canvas, scrollable_frame):
        """Setup enhanced scrolling for menu components with comprehensive event binding"""
        # Bind mouse wheel events to canvas
        canvas.bind("<MouseWheel>", self._on_mousewheel)
        canvas.bind("<Button-4>", self._on_mousewheel)
        canvas.bind("<Button-5>", self._on_mousewheel)

        # Bind scrolling to the main menu frame so scrolling works anywhere in the menu area
        left_frame.bind("<MouseWheel>", self._on_mousewheel)
        left_frame.bind("<Button-4>", self._on_mousewheel)
        left_frame.bind("<Button-5>", self._on_mousewheel)

        # Bind scrolling to the items frame
        items_frame.bind("<MouseWheel>", self._on_mousewheel)
        items_frame.bind("<Button-4>", self._on_mousewheel)
        items_frame.bind("<Button-5>", self._on_mousewheel)

        # Bind scrolling to the scrollable frame
        scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
        scrollable_frame.bind("<Button-4>", self._on_mousewheel)
        scrollable_frame.bind("<Button-5>", self._on_mousewheel)

        # Bind scrolling to categories frame
        if hasattr(self, 'categories_frame') and self.categories_frame:
            self.categories_frame.bind("<MouseWheel>", self._on_mousewheel)
            self.categories_frame.bind("<Button-4>", self._on_mousewheel)
            self.categories_frame.bind("<Button-5>", self._on_mousewheel)

        # Enhanced binding function that recursively binds to all child widgets
        def bind_scrolling_recursively(widget):
            """Recursively bind scroll events to all widgets in the menu area"""
            try:
                # Bind scroll events to current widget
                widget.bind("<MouseWheel>", self._on_mousewheel)
                widget.bind("<Button-4>", self._on_mousewheel)
                widget.bind("<Button-5>", self._on_mousewheel)

                # For touchpad support
                widget.bind("<Shift-MouseWheel>", self._on_horizontal_scroll)

                # Recursively bind to all children
                for child in widget.winfo_children():
                    bind_scrolling_recursively(child)
            except:
                # Ignore widgets that don't support event binding
                pass

        # Apply enhanced binding to the entire menu area
        def apply_enhanced_binding():
            bind_scrolling_recursively(left_frame)
            bind_scrolling_recursively(items_frame)
            bind_scrolling_recursively(canvas)
            bind_scrolling_recursively(scrollable_frame)

            # Re-apply binding periodically to catch dynamically created widgets
            left_frame.after(1000, apply_enhanced_binding)

        # Schedule initial binding after widgets are created
        left_frame.after(100, apply_enhanced_binding)

        # Focus handling to ensure scroll events are captured
        def on_enter(event):
            """Set focus when mouse enters the menu area"""
            try:
                canvas.focus_set()
            except:
                pass

        # Bind focus events to ensure scroll events work
        canvas.bind("<Enter>", on_enter)
        items_frame.bind("<Enter>", on_enter)
        left_frame.bind("<Enter>", on_enter)

        # Update scroll region after setup
        canvas.after(50, lambda: self._update_scroll_region())
