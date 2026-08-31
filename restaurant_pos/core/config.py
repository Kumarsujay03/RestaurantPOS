"""
Restaurant Configuration
Define your restaurant details here - they will be used throughout the system
"""

# Restaurant Information
# Update these values with your own restaurant details.
RESTAURANT_CONFIG = {
    "name": "My Restaurant",
    "address": "123 Main Street, City, State, 000000",
    "phone": "0000000000",
    "email": "contact@example.com",
    "owner": "Owner Name",
    "gst_number": "GST000000000",  # Optional
    "established": "2025",
    "tagline": "Good food, good mood!"
}

# Display Settings
DISPLAY_CONFIG = {
    "show_gst": False,
    "show_email": True,
    "show_established": True,
    "show_tagline": True,
    "currency_symbol": "₹",
    "date_format": "%Y-%m-%d",
    "time_format": "%H:%M:%S"
}

# Bill Settings
BILL_CONFIG = {
    "bill_prefix": "BILL",
    "footer_message": "Thank you for dining with us!\nPlease visit again!\nBanquet hall opening soon!",
    "include_service_charge": False,
    "service_charge_percentage": 10.0,
    "include_gst": False,
    "gst_percentage": 18.0
}

def get_restaurant_name():
    """Get the restaurant name"""
    return RESTAURANT_CONFIG["name"]

def get_restaurant_address():
    """Get the restaurant address"""
    return RESTAURANT_CONFIG["address"]

def get_restaurant_phone():
    """Get the restaurant phone number"""
    return RESTAURANT_CONFIG["phone"]

def get_restaurant_email():
    """Get the restaurant email"""
    return RESTAURANT_CONFIG["email"]

def get_full_restaurant_info():
    """Get complete restaurant information"""
    return RESTAURANT_CONFIG

def get_bill_header():
    """Get formatted bill header"""
    header = f"{RESTAURANT_CONFIG['name']}\n"
    header += f"{RESTAURANT_CONFIG['address']}\n"
    header += f"Phone: {RESTAURANT_CONFIG['phone']}"

    if DISPLAY_CONFIG["show_email"]:
        header += f" | Email: {RESTAURANT_CONFIG['email']}"

    if DISPLAY_CONFIG["show_gst"] and RESTAURANT_CONFIG.get("gst_number"):
        header += f"\nGST No: {RESTAURANT_CONFIG['gst_number']}"

    if DISPLAY_CONFIG["show_tagline"]:
        header += f"\n{RESTAURANT_CONFIG['tagline']}"

    return header

def get_bill_footer():
    """Get formatted bill footer"""
    return BILL_CONFIG["footer_message"]

def get_currency_symbol():
    """Get currency symbol"""
    return DISPLAY_CONFIG["currency_symbol"]

def get_bill_prefix():
    """Get bill number prefix"""
    return BILL_CONFIG["bill_prefix"]
