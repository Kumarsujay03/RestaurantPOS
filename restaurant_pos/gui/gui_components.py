"""
GUI Components Module
Contains reusable GUI components and utilities
"""
import tkinter as tk
from tkinter import ttk

class StyleManager:
    """Manages GUI styles and themes with responsive design"""

    @staticmethod
    def setup_styles():
        """Setup custom styles for the application with responsive sizing optimized for 1024x768"""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure responsive styles
        style.configure('Title.TLabel',
                       font=('Arial', 16, 'bold'),
                       background='#f0f0f0')

        style.configure('Header.TLabel',
                       font=('Arial', 12, 'bold'),
                       background='#f0f0f0')

        style.configure('Total.TLabel',
                       font=('Arial', 14, 'bold'),
                       background='#f0f0f0',
                       foreground='#d63384')

        # Action buttons with normal (non-bold) font weight
        style.configure('Action.TButton',
                       font=('Arial', 11, 'bold'),
                       padding=(12, 8),
                       relief='raised',
                       borderwidth=2)

        style.map('Action.TButton',
                 background=[('active', '#e3f2fd'),
                           ('pressed', '#bbdefb')])

        # Compact category buttons - smaller size for better fit
        style.configure('Category.TButton',
                       font=('Arial', 9, 'bold'),
                       padding=(6, 4),
                       relief='raised',
                       borderwidth=2)

        style.map('Category.TButton',
                 background=[('active', '#f3e5f5'),
                           ('pressed', '#e1bee7')],
                 relief=[('pressed', 'sunken')])

        # Menu item buttons - better wrapping for longer names
        style.configure('Item.TButton',
                       font=('Arial', 9, 'bold'),
                       padding=(6, 4),
                       relief='raised',
                       borderwidth=1,
                       wraplength=90)

        style.map('Item.TButton',
                 background=[('active', '#e8f5e8'),
                           ('pressed', '#c8e6c9'),
                           ('disabled', '#f5f5f5')],
                 foreground=[('disabled', '#999999')],
                 relief=[('pressed', 'sunken')])

        # Menu item buttons for individual category view - better wrapping for longer names
        style.configure('ItemSmall.TButton',
                       font=('Arial', 9, 'bold'),
                       padding=(6, 4),
                       relief='raised',
                       borderwidth=1,
                       wraplength=90)

        style.map('ItemSmall.TButton',
                 background=[('active', '#e8f5e8'),
                           ('pressed', '#c8e6c9'),
                           ('disabled', '#f5f5f5')],
                 foreground=[('disabled', '#999999')],
                 relief=[('pressed', 'sunken')])

        # Enhanced frame styles
        style.configure('Card.TLabelFrame',
                       relief='raised',
                       borderwidth=1,
                       padding=10)

        # Responsive treeview style
        style.configure('Treeview.Heading',
                       font=('Arial', 10, 'bold'),
                       relief='raised')

        style.configure('Treeview',
                       font=('Arial', 10),
                       rowheight=24)

    @staticmethod
    def get_responsive_font_size(base_size, screen_category):
        """Get responsive font size based on screen category"""
        if screen_category == "large":
            return base_size + 1
        elif screen_category == "small":
            return max(8, base_size - 1)
        return base_size

    @staticmethod
    def get_responsive_padding(base_padding, screen_category):
        """Get responsive padding based on screen category"""
        if screen_category == "large":
            return base_padding + 2
        elif screen_category == "small":
            return max(2, base_padding - 2)
        return base_padding

class TooltipManager:
    """Manages tooltips for GUI elements"""

    @staticmethod
    def create_tooltip(widget, text):
        """Create a tooltip for a widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, background="lightyellow",
                           relief="solid", borderwidth=1, font=("Arial", 8))
            label.pack()
            widget.tooltip = tooltip

        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

class TimeDisplay:
    """Manages time display functionality"""

    def __init__(self, parent_widget):
        self.time_label = parent_widget
        self.update_time()

    def update_time(self):
        """Update the current time display"""
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.time_label.after(1000, self.update_time)
