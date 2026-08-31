"""
Path utilities for the Restaurant POS System
Ensures all files are created relative to the executable location
"""
import os
import sys
from pathlib import Path

def get_app_directory():
    """
    Get the base directory used to store the database and generated bills.

    Works both in development and when compiled with PyInstaller. In
    development this resolves to the project root (the folder that contains
    the ``restaurant_pos`` package), regardless of where this module lives
    inside the package.
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return os.path.dirname(sys.executable)

    # Running as a Python script in development.
    # This file lives at: <root>/restaurant_pos/core/path_utils.py
    # so the project root is three levels up from this file.
    module_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(module_dir, "..", ".."))

def get_database_path():
    """Get the full path to the restaurant database file"""
    app_dir = get_app_directory()
    return os.path.join(app_dir, "restaurant.db")

def get_bills_directory():
    """Get the full path to the bills directory and create it if it doesn't exist"""
    app_dir = get_app_directory()
    bills_dir = os.path.join(app_dir, "bills")

    # Create bills directory if it doesn't exist
    if not os.path.exists(bills_dir):
        os.makedirs(bills_dir)
        print(f"📁 Created bills directory: {bills_dir}")

    return bills_dir

def get_bill_file_path(bill_number, date_str, extension="pdf"):
    """
    Get the full path for a bill file
    Args:
        bill_number: The bill number (e.g., "BILL20250729134317")
        date_str: The date string (e.g., "20250729")
        extension: File extension without dot (default: "pdf")
    """
    bills_dir = get_bills_directory()
    filename = f"bill_{bill_number}_{date_str}.{extension}"
    return os.path.join(bills_dir, filename)

def ensure_app_directories():
    """
    Ensure all required application directories exist.
    This should be called at application startup.
    """
    app_dir = get_app_directory()
    print(f"📍 Application directory: {app_dir}")

    # Ensure bills directory exists
    bills_dir = get_bills_directory()

    # Ensure database directory is accessible (database file will be created by DatabaseManager)
    db_path = get_database_path()
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        print(f"📁 Created database directory: {db_dir}")

    print(f"📁 Bills directory: {bills_dir}")
    print(f"🗄️ Database path: {db_path}")

    return {
        'app_dir': app_dir,
        'bills_dir': bills_dir,
        'database_path': db_path
    }

def is_directory_writable(directory_path):
    """Check if a directory is writable"""
    try:
        test_file = os.path.join(directory_path, "test_write.tmp")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        return True
    except:
        return False

def get_fallback_directory():
    """Get a fallback directory if the app directory is not writable"""
    import tempfile
    return tempfile.gettempdir()
