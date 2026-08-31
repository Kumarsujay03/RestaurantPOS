import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

class ManagementInterface:
    def __init__(self, parent, food_manager):
        self.parent = parent
        self.food_manager = food_manager
        self.window = None

    def show_management_window(self):
        """Show the main management window"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return

        self.window = tk.Toplevel(self.parent)
        self.window.title("Restaurant Management System")

        # Make window responsive to screen size
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        # Calculate responsive window size
        window_width = min(max(800, int(screen_width * 0.7)), screen_width - 200)
        window_height = min(max(600, int(screen_height * 0.8)), screen_height - 150)

        # Center the window on parent
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2

        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.window.minsize(700, 500)  # Set minimum size
        self.window.resizable(True, True)  # Make resizable

        self.window.transient(self.parent)
        self.window.grab_set()

        # Configure window for responsiveness
        self.window.configure(bg='#f0f0f0')
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)

        # Main frame
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="🏪 Restaurant Management System",
                               font=('Arial', 18, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 20))

        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))

        # Category Management Tab
        self.create_category_tab(notebook)

        # Menu Item Management Tab
        self.create_menu_tab(notebook)

        # Statistics Tab
        self.create_statistics_tab(notebook)

        # Close button
        close_btn = ttk.Button(main_frame, text="Close",
                              command=self.window.destroy,
                              style='Action.TButton')
        close_btn.grid(row=2, column=0, pady=(10, 0))

    def center_window(self):
        """Center the management window on parent"""
        self.window.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - 800) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - 600) // 2
        self.window.geometry(f"800x600+{x}+{y}")

    def create_category_tab(self, notebook):
        """Create category management tab"""
        category_frame = ttk.Frame(notebook)
        notebook.add(category_frame, text="📂 Categories")

        # Main container
        container = ttk.Frame(category_frame, padding="20")
        container.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(container, text="Category Management",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))

        # Left side - Category list
        left_frame = ttk.Frame(container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))

        # Category listbox with scrollbar
        list_frame = ttk.LabelFrame(left_frame, text="Categories", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.category_listbox = tk.Listbox(list_frame, font=('Arial', 11), height=15)
        category_scrollbar = ttk.Scrollbar(list_frame, orient="vertical",
                                         command=self.category_listbox.yview)
        self.category_listbox.configure(yscrollcommand=category_scrollbar.set)

        self.category_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        category_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Right side - Controls
        right_frame = ttk.Frame(container)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Category controls
        controls_frame = ttk.LabelFrame(right_frame, text="Actions", padding="10")
        controls_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Button(controls_frame, text="➕ Add Category",
                  command=self.add_category,
                  style='Action.TButton').pack(fill=tk.X, pady=5)

        ttk.Button(controls_frame, text="✏️ Edit Category",
                  command=self.edit_category,
                  style='Action.TButton').pack(fill=tk.X, pady=5)

        ttk.Button(controls_frame, text="🗑️ Delete Category",
                  command=self.delete_category,
                  style='Action.TButton').pack(fill=tk.X, pady=5)

        ttk.Button(controls_frame, text="📊 Category Stats",
                  command=self.show_category_stats,
                  style='Action.TButton').pack(fill=tk.X, pady=5)

        ttk.Button(controls_frame, text="🔄 Refresh",
                  command=self.refresh_categories,
                  style='Action.TButton').pack(fill=tk.X, pady=5)

        # Load categories
        self.refresh_categories()

    def create_menu_tab(self, notebook):
        """Create menu item management tab"""
        menu_frame = ttk.Frame(notebook)
        notebook.add(menu_frame, text="🍽️ Menu Items")

        # Main container
        container = ttk.Frame(menu_frame, padding="20")
        container.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(container, text="Menu Item Management",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))

        # Left side - Menu items
        left_frame = ttk.Frame(container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))

        # Menu items treeview
        tree_frame = ttk.LabelFrame(left_frame, text="Menu Items", padding="10")
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Create treeview
        columns = ('name', 'category', 'price', 'status')
        self.menu_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)

        # Configure columns
        self.menu_tree.heading('name', text='Item Name')
        self.menu_tree.heading('category', text='Category')
        self.menu_tree.heading('price', text='Price')
        self.menu_tree.heading('status', text='Status')

        self.menu_tree.column('name', width=200)
        self.menu_tree.column('category', width=120)
        self.menu_tree.column('price', width=80)
        self.menu_tree.column('status', width=80)

        # Add scrollbar
        menu_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical",
                                      command=self.menu_tree.yview)
        self.menu_tree.configure(yscrollcommand=menu_scrollbar.set)

        self.menu_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        menu_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Right side - Controls
        right_frame = ttk.Frame(container)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Menu controls
        controls_frame = ttk.LabelFrame(right_frame, text="Actions", padding="10")
        controls_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Button(controls_frame, text="➕ Add Item",
                  command=self.add_menu_item,
                  style='Action.TButton').pack(fill=tk.X, pady=5)

        ttk.Button(controls_frame, text="✏️ Edit Item",
                  command=self.edit_menu_item,
                  style='Action.TButton').pack(fill=tk.X, pady=5)

        ttk.Button(controls_frame, text="🗑️ Delete Item",
                  command=self.delete_menu_item,
                  style='Action.TButton').pack(fill=tk.X, pady=5)

        ttk.Button(controls_frame, text="🔄 Refresh",
                  command=self.refresh_menu_items,
                  style='Action.TButton').pack(fill=tk.X, pady=5)

        # Load menu items
        self.refresh_menu_items()

    def create_statistics_tab(self, notebook):
        """Create statistics tab"""
        stats_frame = ttk.Frame(notebook)
        notebook.add(stats_frame, text="📊 Statistics")

        # Main container
        container = ttk.Frame(stats_frame, padding="20")
        container.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(container, text="Restaurant Statistics",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))

        # Statistics display
        self.create_statistics_display(container)

    def create_statistics_display(self, parent):
        """Create statistics display"""
        # Overall stats frame
        overall_frame = ttk.LabelFrame(parent, text="Overall Statistics", padding="10")
        overall_frame.pack(fill=tk.X, pady=(0, 20))

        # Get statistics
        categories = self.food_manager.get_categories()
        total_categories = len(categories)

        all_items = self.food_manager.get_all_items()
        total_items = len(all_items)
        available_items = sum(1 for item in all_items if item.get('available', True))

        # Display stats
        stats_text = f"""
        Total Categories: {total_categories}
        Total Menu Items: {total_items}
        Available Items: {available_items}
        Unavailable Items: {total_items - available_items}
        """

        ttk.Label(overall_frame, text=stats_text, font=('Arial', 12)).pack(anchor=tk.W)

        # Category-wise stats
        category_stats_frame = ttk.LabelFrame(parent, text="Category Statistics", padding="10")
        category_stats_frame.pack(fill=tk.BOTH, expand=True)

        # Create treeview for category stats
        columns = ('category', 'items', 'available', 'unavailable')
        stats_tree = ttk.Treeview(category_stats_frame, columns=columns, show='headings', height=10)

        stats_tree.heading('category', text='Category')
        stats_tree.heading('items', text='Total Items')
        stats_tree.heading('available', text='Available')
        stats_tree.heading('unavailable', text='Unavailable')

        # Add data
        for category in categories:
            items = self.food_manager.get_items_by_category(category)
            total = len(items)
            available = sum(1 for item in items if item.get('available', True))
            unavailable = total - available

            stats_tree.insert('', 'end', values=(category, total, available, unavailable))

        stats_tree.pack(fill=tk.BOTH, expand=True)

    # Category Management Methods
    def refresh_categories(self):
        """Refresh category list"""
        self.category_listbox.delete(0, tk.END)
        categories = self.food_manager.get_categories()
        for category in categories:
            self.category_listbox.insert(tk.END, category)

    def add_category(self):
        """Add new category"""
        dialog = CategoryDialog(self.window, "Add Category", self.food_manager)
        if dialog.result:
            self.refresh_categories()
            messagebox.showinfo("Success", "Category added successfully!")

    def edit_category(self):
        """Edit selected category"""
        selection = self.category_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a category to edit")
            return

        category = self.category_listbox.get(selection[0])
        dialog = CategoryEditDialog(self.window, f"Edit Category: {category}",
                                  self.food_manager, category)
        if dialog.result:
            self.refresh_categories()
            messagebox.showinfo("Success", "Category updated successfully!")

    def delete_category(self):
        """Delete selected category"""
        selection = self.category_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a category to delete")
            return

        category = self.category_listbox.get(selection[0])

        # Count items in category
        items = self.food_manager.get_items_by_category(category)
        item_count = len(items)

        if messagebox.askyesno("Confirm Deletion",
                             f"Are you sure you want to delete '{category}'?\n\n"
                             f"This will also delete {item_count} item(s) in this category.\n"
                             f"This action cannot be undone!"):
            if self.food_manager.remove_category(category):
                self.refresh_categories()
                self.refresh_menu_items()
                messagebox.showinfo("Success", f"Category '{category}' deleted successfully!")
            else:
                messagebox.showerror("Error", "Failed to delete category")

    def show_category_stats(self):
        """Show statistics for selected category"""
        selection = self.category_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a category to view stats")
            return

        category = self.category_listbox.get(selection[0])
        items = self.food_manager.get_items_by_category(category)

        if not items:
            messagebox.showinfo("No Items", f"No items found in category '{category}'")
            return

        # Show detailed stats window
        self.show_detailed_category_stats(category, items)

    def show_detailed_category_stats(self, category, items):
        """Show detailed category statistics"""
        stats_window = tk.Toplevel(self.window)
        stats_window.title(f"Statistics for '{category}'")
        stats_window.geometry("600x500")
        stats_window.transient(self.window)
        stats_window.grab_set()

        main_frame = ttk.Frame(stats_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(main_frame, text=f"Category: {category}",
                 font=('Arial', 16, 'bold')).pack(pady=(0, 20))

        # Statistics
        total_items = len(items)
        available_items = sum(1 for item in items if item.get('available', True))
        unavailable_items = total_items - available_items
        total_value = sum(item['price'] for item in items)
        avg_price = total_value / total_items if total_items > 0 else 0

        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding="10")
        stats_frame.pack(fill=tk.X, pady=(0, 20))

        stats_text = f"""
        Total Items: {total_items}
        Available Items: {available_items}
        Unavailable Items: {unavailable_items}
        Total Value: ₹{total_value:.2f}
        Average Price: ₹{avg_price:.2f}
        """

        ttk.Label(stats_frame, text=stats_text, font=('Arial', 12)).pack(anchor=tk.W)

        # Items list
        items_frame = ttk.LabelFrame(main_frame, text="Items in Category", padding="10")
        items_frame.pack(fill=tk.BOTH, expand=True)

        columns = ('name', 'price', 'status')
        tree = ttk.Treeview(items_frame, columns=columns, show='headings', height=10)

        tree.heading('name', text='Item Name')
        tree.heading('price', text='Price')
        tree.heading('status', text='Status')

        for item in items:
            status = "Available" if item.get('available', True) else "Unavailable"
            tree.insert('', 'end', values=(item['name'], f"₹{item['price']:.2f}", status))

        tree.pack(fill=tk.BOTH, expand=True)

        # Close button
        ttk.Button(main_frame, text="Close", command=stats_window.destroy).pack(pady=(10, 0))

    # Menu Item Management Methods
    def refresh_menu_items(self):
        """Refresh menu items list"""
        # Clear existing items
        for item in self.menu_tree.get_children():
            self.menu_tree.delete(item)

        # Add items
        items = self.food_manager.get_all_items()
        for item in items:
            status = "Available" if item.get('available', True) else "Unavailable"
            self.menu_tree.insert('', 'end', values=(
                item['name'],
                item['category'],
                f"₹{item['price']:.2f}",
                status
            ))

    def add_menu_item(self):
        """Add new menu item"""
        dialog = MenuItemDialog(self.window, "Add Menu Item", self.food_manager)
        if dialog.result:
            self.refresh_menu_items()
            messagebox.showinfo("Success", "Menu item added successfully!")

    def edit_menu_item(self):
        """Edit selected menu item"""
        selection = self.menu_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a menu item to edit")
            return

        item_values = self.menu_tree.item(selection[0])['values']
        item_name = item_values[0]

        # Find the item in the database
        items = self.food_manager.get_all_items()
        selected_item = None
        for item in items:
            if item['name'] == item_name:
                selected_item = item
                break

        if selected_item:
            dialog = MenuItemEditDialog(self.window, "Edit Menu Item",
                                      self.food_manager, selected_item)
            if dialog.result:
                self.refresh_menu_items()
                messagebox.showinfo("Success", "Menu item updated successfully!")
        else:
            messagebox.showerror("Error", "Item not found")

    def delete_menu_item(self):
        """Delete selected menu item"""
        selection = self.menu_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a menu item to delete")
            return

        item_values = self.menu_tree.item(selection[0])['values']
        item_name = item_values[0]

        if messagebox.askyesno("Confirm Deletion",
                             f"Are you sure you want to delete '{item_name}'?\n"
                             f"This action cannot be undone!"):
            # Find and delete the item
            items = self.food_manager.get_all_items()
            for item in items:
                if item['name'] == item_name:
                    if self.food_manager.remove_food_item(item['id']):
                        self.refresh_menu_items()
                        messagebox.showinfo("Success", f"Item '{item_name}' deleted successfully!")
                    else:
                        messagebox.showerror("Error", "Failed to delete item")
                    return

            messagebox.showerror("Error", "Item not found")


# Dialog Classes
class CategoryDialog:
    def __init__(self, parent, title, food_manager):
        self.result = None
        self.food_manager = food_manager

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.create_widgets()
        self.dialog.wait_window()

    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Category Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, pady=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Add Category", command=self.add_category).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

    def add_category(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a category name")
            return

        if self.food_manager.add_category(name):
            self.result = True
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to add category")


class CategoryEditDialog:
    def __init__(self, parent, title, food_manager, category):
        self.result = None
        self.food_manager = food_manager
        self.category = category

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.create_widgets()
        self.dialog.wait_window()

    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Category Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar(value=self.category)
        ttk.Entry(main_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, pady=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Save Changes", command=self.save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

    def save_changes(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a category name")
            return

        if self.food_manager.update_category(self.category, name):
            self.result = True
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to update category")


class MenuItemDialog:
    def __init__(self, parent, title, food_manager):
        self.result = None
        self.food_manager = food_manager

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.create_widgets()
        self.dialog.wait_window()

    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Item name
        ttk.Label(main_frame, text="Item Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, pady=5)

        # Category
        ttk.Label(main_frame, text="Category:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar()
        categories = self.food_manager.get_categories()
        category_combo = ttk.Combobox(main_frame, textvariable=self.category_var,
                                     values=categories, width=27)
        category_combo.grid(row=1, column=1, pady=5)

        # Price
        ttk.Label(main_frame, text="Price (₹):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.price_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.price_var, width=30).grid(row=2, column=1, pady=5)

        # Available
        ttk.Label(main_frame, text="Available:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.available_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, variable=self.available_var).grid(row=3, column=1, sticky=tk.W, pady=5)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Add Item", command=self.add_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

    def add_item(self):
        name = self.name_var.get().strip()
        category = self.category_var.get().strip()
        price_str = self.price_var.get().strip()

        if not name or not category or not price_str:
            messagebox.showerror("Error", "Please fill all fields")
            return

        try:
            price = float(price_str)
            if price <= 0:
                messagebox.showerror("Error", "Price must be positive")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid price format")
            return

        if self.food_manager.add_food_item(name, category, price, self.available_var.get()):
            self.result = True
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to add item")


class MenuItemEditDialog:
    def __init__(self, parent, title, food_manager, item):
        self.result = None
        self.food_manager = food_manager
        self.item = item

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.create_widgets()
        self.dialog.wait_window()

    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Item name
        ttk.Label(main_frame, text="Item Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar(value=self.item['name'])
        ttk.Entry(main_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, pady=5)

        # Category
        ttk.Label(main_frame, text="Category:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar(value=self.item['category'])
        categories = self.food_manager.get_categories()
        category_combo = ttk.Combobox(main_frame, textvariable=self.category_var,
                                     values=categories, width=27)
        category_combo.grid(row=1, column=1, pady=5)

        # Price
        ttk.Label(main_frame, text="Price (₹):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.price_var = tk.StringVar(value=f"{self.item['price']:.2f}")
        ttk.Entry(main_frame, textvariable=self.price_var, width=30).grid(row=2, column=1, pady=5)

        # Available
        ttk.Label(main_frame, text="Available:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.available_var = tk.BooleanVar(value=self.item.get('available', True))
        ttk.Checkbutton(main_frame, variable=self.available_var).grid(row=3, column=1, sticky=tk.W, pady=5)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Save Changes", command=self.save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

    def save_changes(self):
        name = self.name_var.get().strip()
        category = self.category_var.get().strip()
        price_str = self.price_var.get().strip()

        if not name or not category or not price_str:
            messagebox.showerror("Error", "Please fill all fields")
            return

        try:
            price = float(price_str)
            if price <= 0:
                messagebox.showerror("Error", "Price must be positive")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid price format")
            return

        if self.food_manager.update_food_item(self.item['id'], name, category, price, self.available_var.get()):
            self.result = True
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to update item")
