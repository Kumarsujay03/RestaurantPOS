#!/usr/bin/env python3
"""
Restaurant POS System Launcher
Run this file to start the Point of Sale system
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

def setup_environment():
    """Report runtime environment details (useful for debugging printers)."""
    print("🔧 Setting up environment for printer detection...")

    if hasattr(sys, 'ps1'):
        print("📝 Running from interactive Python shell")
    elif getattr(sys, 'frozen', False):
        print("📦 Running as compiled executable")
    else:
        print("🖥️ Running as Python script")

    print(f"🐍 Python version: {sys.version}")
    print(f"📁 Current working directory: {os.getcwd()}")

def check_printer_environment():
    """Check if printer detection libraries are available"""
    print("🖨️ Checking printer detection environment...")

    try:
        import win32print
        import wmi
        print("✅ Windows printer libraries available")

        # Test basic printer access
        try:
            printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
            print(f"🔍 Found {len(printers)} printer(s) via win32print")
            for printer in printers[:3]:  # Show first 3 printers
                print(f"   - {printer[2]}")
        except Exception as e:
            print(f"⚠️ Error accessing printers: {e}")

    except ImportError as e:
        print(f"❌ Printer libraries not available: {e}")
        print("💡 Try installing: pip install pywin32 wmi")

def main():
    try:
        # Setup environment first
        setup_environment()
        check_printer_environment()

        print("🚀 Starting Restaurant POS System...")

        # Import and run the POS system
        from restaurant_pos.gui.pos_gui import RestaurantPOS

        # Create the main window
        root = tk.Tk()

        # Initialize the POS application (will start in full-screen mode)
        app = RestaurantPOS(root)

        print("✅ POS System initialized successfully")

        # Start the application event loop
        root.mainloop()

    except ImportError as e:
        error_msg = f"Failed to import required modules: {e}\n\nPlease ensure all dependencies are installed:\npip install -r requirements.txt"
        messagebox.showerror("Import Error", error_msg)
        print(f"Import Error: {e}")
        sys.exit(1)
    except Exception as e:
        error_msg = f"An error occurred: {e}\n\nPlease check the console output for more details."
        messagebox.showerror("Error", error_msg)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
