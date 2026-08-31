import os
import sys
import tempfile
from datetime import datetime
from typing import List, Dict, Optional
import subprocess
from pathlib import Path
import platform

# Import path utilities for correct directory handling
from restaurant_pos.core.path_utils import get_bills_directory, get_bill_file_path

# Enhanced printer libraries
try:
    import win32print
    import win32api
    import wmi
    WIN32_AVAILABLE = True
    print("Windows printing libraries successfully imported")
except ImportError as e:
    WIN32_AVAILABLE = False
    print(f"Windows printing libraries not available: {e}")

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
    print("ReportLab successfully imported for PDF generation")
except ImportError as e:
    REPORTLAB_AVAILABLE = False
    print(f"ReportLab import failed: {e}")
    print("PDF generation will fallback to text files")

from restaurant_pos.core.config import get_bill_header, get_bill_footer, get_currency_symbol

class EnhancedBillPrinter:
    def __init__(self):
        self.currency = get_currency_symbol()
        self.temp_dir = tempfile.gettempdir()
        self.physical_printers = []
        self.default_printer = None
        self._detect_physical_printers()

    def _detect_physical_printers(self):
        """Detect all physical printers connected to the system with actual connectivity check"""
        self.physical_printers = []

        if platform.system() == "Windows" and WIN32_AVAILABLE:
            try:
                # Method 1: Use WMI to get detailed printer information with connectivity verification
                try:
                    c = wmi.WMI()
                    for printer in c.Win32_Printer():
                        # Skip if printer is offline or has error status
                        if printer.WorkOffline or printer.PrinterStatus in [None, 3, 4, 5, 6, 7]:  # Error states
                            continue

                        # Check if it's a physical printer (not virtual/software printer)
                        if not any(virtual in printer.Name.lower() for virtual in
                                 ['pdf', 'xps', 'fax', 'onenote', 'virtual', 'microsoft', 'send to']):

                            # Additional connectivity check - try to verify printer is actually reachable
                            is_connected = self._verify_printer_connectivity(printer.Name)

                            if is_connected:
                                printer_info = {
                                    'name': printer.Name,
                                    'status': printer.PrinterStatus,
                                    'state': printer.PrinterState,
                                    'online': True,
                                    'default': printer.Default
                                }
                                self.physical_printers.append(printer_info)
                                if printer.Default:
                                    self.default_printer = printer_info
                                print(f"Found connected physical printer: {printer.Name} (Status: {printer.PrinterStatus})")
                            else:
                                print(f"Printer {printer.Name} driver found but not physically connected")
                except Exception as e:
                    print(f"WMI printer detection failed: {e}")

                # Method 2: Fallback to win32print with connectivity verification
                if not self.physical_printers:
                    try:
                        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
                        for printer in printers:
                            printer_name = printer[2]
                            if not any(virtual in printer_name.lower() for virtual in
                                     ['pdf', 'xps', 'fax', 'onenote', 'virtual', 'microsoft', 'send to']):

                                # Verify actual connectivity
                                if self._verify_printer_connectivity(printer_name):
                                    self.physical_printers.append({
                                        'name': printer_name,
                                        'status': 'Available',
                                        'online': True,
                                        'default': False
                                    })
                                    print(f"Found connected physical printer via win32print: {printer_name}")
                                else:
                                    print(f"Printer {printer_name} driver found but not physically connected")
                    except Exception as e:
                        print(f"win32print enumeration failed: {e}")

                # Get default printer if not already set
                if not self.default_printer and self.physical_printers:
                    try:
                        default_name = win32print.GetDefaultPrinter()
                        for printer in self.physical_printers:
                            if printer['name'] == default_name:
                                printer['default'] = True
                                self.default_printer = printer
                                break
                    except Exception as e:
                        print(f"Could not get default printer: {e}")
                        # Use first available printer as default
                        if self.physical_printers:
                            self.physical_printers[0]['default'] = True
                            self.default_printer = self.physical_printers[0]
            except Exception as e:
                print(f"Windows printer detection failed: {e}")

        else:
            # For Linux/Mac systems with connectivity check
            try:
                result = subprocess.run(['lpstat', '-p'], capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if line.startswith('printer') and 'idle' in line:  # Only include idle/ready printers
                            printer_name = line.split()[1]
                            self.physical_printers.append({
                                'name': printer_name,
                                'status': 'Available',
                                'online': True,
                                'default': False
                            })
            except Exception as e:
                print(f"Linux printer detection failed: {e}")

        print(f"Total physically connected printers detected: {len(self.physical_printers)}")
        for printer in self.physical_printers:
            print(f"  - {printer['name']} ({'Default' if printer.get('default') else 'Available'})")

    def _verify_printer_connectivity(self, printer_name):
        """Verify if a printer is actually connected and responsive"""
        try:
            # Method 1: Try to open printer handle
            if WIN32_AVAILABLE:
                try:
                    handle = win32print.OpenPrinter(printer_name)
                    if handle:
                        # Get printer info to verify it's accessible
                        printer_info = win32print.GetPrinter(handle, 2)
                        win32print.ClosePrinter(handle)

                        # Check printer status - ensure it's not offline or in error state
                        status = printer_info.get('Status', 0)
                        attributes = printer_info.get('Attributes', 0)

                        # Status 0 means ready, other values indicate problems
                        # Attributes with PRINTER_ATTRIBUTE_WORK_OFFLINE (0x400) means offline
                        if status == 0 and not (attributes & 0x400):
                            return True
                        else:
                            print(f"Printer {printer_name} status: {status}, attributes: {attributes}")
                            return False
                except Exception as e:
                    print(f"Failed to verify printer {printer_name}: {e}")
                    return False

            # Method 2: Fallback - assume printer is available if driver exists
            return True

        except Exception as e:
            print(f"Printer connectivity check failed for {printer_name}: {e}")
            return False

    def refresh_printer_list(self):
        """Refresh the list of available printers"""
        print("🔄 Refreshing printer list...")
        self._detect_physical_printers()
        print(f"✅ Found {len(self.physical_printers)} physical printer(s)")

    def is_physical_printer_available(self) -> bool:
        """Check if any physical printer is available"""
        return len(self.physical_printers) > 0

    def get_available_printers(self) -> List[Dict]:
        """Get list of available physical printers"""
        return self.physical_printers.copy()

    def get_default_printer(self) -> Optional[Dict]:
        """Get the default printer"""
        return self.default_printer

    def print_bill_enhanced(self, bill_data: Dict, print_format='auto') -> bool:
        """
        Enhanced bill printing with better error handling for built applications
        """
        print("🖨️ Starting enhanced bill printing...")

        try:
            # Ensure we have current printer list
            self.refresh_printer_list()

            if not self.is_physical_printer_available():
                print("❌ No physical printers available for printing")
                return False

            # Generate bill content
            bill_content = self._generate_bill_content(bill_data)

            # Try multiple printing methods
            print_success = False

            # Method 1: Try PDF printing (preferred for built apps)
            if REPORTLAB_AVAILABLE:
                try:
                    print("📄 Attempting PDF printing...")
                    if self._print_as_pdf(bill_data, bill_content):
                        print_success = True
                        print("✅ PDF printing successful")
                    else:
                        print("⚠️ PDF printing failed, trying alternative methods...")
                except Exception as e:
                    print(f"❌ PDF printing error: {e}")

            # Method 2: Try direct text printing if PDF failed
            if not print_success:
                try:
                    print("📝 Attempting direct text printing...")
                    if self._print_text_direct(bill_content):
                        print_success = True
                        print("✅ Direct text printing successful")
                except Exception as e:
                    print(f"❌ Direct text printing error: {e}")

            # Method 3: Fallback to system print command
            if not print_success and platform.system() == "Windows":
                try:
                    print("🔧 Attempting system print command...")
                    if self._print_via_system_command(bill_content, bill_data):
                        print_success = True
                        print("✅ System print command successful")
                except Exception as e:
                    print(f"❌ System print command error: {e}")

            return print_success

        except Exception as e:
            print(f"❌ Bill printing failed: {e}")
            return False

    def _print_via_system_command(self, bill_content: str, bill_data: Dict) -> bool:
        """Print using Windows system print command as fallback"""
        try:
            # Create temporary text file
            bill_number = bill_data.get('bill_number', 'TEMP')
            date_str = datetime.now().strftime("%Y%m%d")

            # Use bills directory for temp file
            bills_dir = get_bills_directory()
            temp_file = os.path.join(bills_dir, f"temp_bill_{bill_number}.txt")

            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(bill_content)

            # Get default printer name
            default_printer = None
            if self.default_printer:
                default_printer = self.default_printer['name']
            elif self.physical_printers:
                default_printer = self.physical_printers[0]['name']

            if default_printer:
                # Use Windows print command
                cmd = f'print /D:"{default_printer}" "{temp_file}"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                # Clean up temp file
                try:
                    os.remove(temp_file)
                except:
                    pass

                if result.returncode == 0:
                    print(f"✅ System print command executed successfully to {default_printer}")
                    return True
                else:
                    print(f"❌ System print command failed: {result.stderr}")
                    return False
            else:
                print("❌ No default printer found for system command")
                return False

        except Exception as e:
            print(f"❌ System print command error: {e}")
            return False

    def create_bill_content(self, bill_number: str, customer_name: str, bill_items: List[Dict],
                           total_amount: float, date: str, time: str) -> str:
        """Create formatted bill content optimized for half A4 (A5) paper with A5 centered format"""
        header = get_bill_header()
        footer = get_bill_footer()

        bill_content = []

        # A5 right-shifted formatting specifications for half A4 paper
        content_width = 24  # Reduced content width for safety
        paper_width = 80    # Full printer width (characters)
        # Increased left margin significantly to shift content to right side
        left_margin = 35    # Much larger margin to avoid left cutoff
        margin_spaces = " " * left_margin

        # Helper function to center content within the content area
        def center_line(text, width=content_width):
            return f"{text:^{width}}"

        def left_align_line(text, width=content_width):
            return f"{text:<{width}}"

        def right_align_line(text, width=content_width):
            return f"{text:>{width}}"

        def wrap_text(text, max_width):
            """Wrap text to multiple lines with proper word breaking"""
            if len(text) <= max_width:
                return [text]

            words = text.split()
            lines = []
            current_line = ""

            for word in words:
                if len(current_line + " " + word) <= max_width:
                    current_line += (" " + word if current_line else word)
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word

                    # If single word is too long, break it
                    if len(current_line) > max_width:
                        while len(current_line) > max_width:
                            lines.append(current_line[:max_width])
                            current_line = current_line[max_width:]

            if current_line:
                lines.append(current_line)

            return lines

        # Start immediately at the very top - no blank lines or spacing above
        # Restaurant header begins at line 1
        header_lines = header.split('\n')
        for line in header_lines:
            if line.strip():
                if len(line) <= content_width:
                    bill_content.append(margin_spaces + center_line(line))
                else:
                    # Split long lines
                    words = line.split()
                    current_line = ""
                    for word in words:
                        if len(current_line + " " + word) <= content_width:
                            current_line += (" " + word if current_line else word)
                        else:
                            if current_line:
                                bill_content.append(margin_spaces + center_line(current_line))
                            current_line = word
                    if current_line:
                        bill_content.append(margin_spaces + center_line(current_line))

        # Add separator line only after header content
        bill_content.append(margin_spaces + "=" * content_width)

        # Bill details - left aligned within centered area
        bill_content.append(margin_spaces + left_align_line(f"Bill: {bill_number[:18]}"))

        customer_display = f"Customer: {customer_name}"
        if len(customer_display) > content_width:
            customer_display = f"Cust: {customer_name[:18]}"
        bill_content.append(margin_spaces + left_align_line(customer_display[:content_width]))

        bill_content.append(margin_spaces + left_align_line(f"Date: {date}"))
        bill_content.append(margin_spaces + left_align_line(f"Time: {time}"))
        bill_content.append(margin_spaces + "-" * content_width)

        # Items header - adjusted for better layout with wider item names
        header_line = f"{'Item':<14} {'Q':<1} {'Price':<3} {'Total':<4}"
        bill_content.append(margin_spaces + left_align_line(header_line))
        bill_content.append(margin_spaces + "-" * content_width)

        # Items with proper formatting and multi-line support for long names
        for item in bill_items:
            item_name = item['name']
            qty = str(item['quantity'])
            price = f"{item['price']:.0f}"[:3]  # Limit price to 3 characters
            total = f"{item['total']:.0f}"[:4]  # Limit total to 4 characters

            # Check if item name fits in allocated space (14 characters)
            if len(item_name) <= 14:
                # Single line item
                item_line = f"{item_name:<14} {qty:<1} {price:<3} {total:<4}"
                bill_content.append(margin_spaces + left_align_line(item_line))
            else:
                # Multi-line item - wrap the name
                name_lines = wrap_text(item_name, 14)

                # First line with all details
                first_line = f"{name_lines[0]:<14} {qty:<1} {price:<3} {total:<4}"
                bill_content.append(margin_spaces + left_align_line(first_line))

                # Additional lines for remaining name parts (indented slightly)
                for name_line in name_lines[1:]:
                    continued_line = f"  {name_line:<12}        "  # Indent and fill remaining space
                    bill_content.append(margin_spaces + left_align_line(continued_line))

        bill_content.append(margin_spaces + "-" * content_width)

        # Total line - right aligned
        total_line = f"TOTAL: Rs{total_amount:.0f}"
        bill_content.append(margin_spaces + right_align_line(total_line))
        bill_content.append(margin_spaces + "=" * content_width)
        bill_content.append(margin_spaces + "")  # Empty line

        # Footer - centered
        footer_lines = footer.split('\n')
        for line in footer_lines:
            if line.strip():
                if len(line) <= content_width:
                    bill_content.append(margin_spaces + center_line(line))
                else:
                    # Split long footer lines
                    words = line.split()
                    current_line = ""
                    for word in words:
                        if len(current_line + " " + word) <= content_width:
                            current_line += (" " + word if current_line else word)
                        else:
                            if current_line:
                                bill_content.append(margin_spaces + center_line(current_line))
                            current_line = word
                    if current_line:
                        bill_content.append(margin_spaces + center_line(current_line))

        bill_content.append(margin_spaces + "=" * content_width)
        bill_content.append("")  # Final empty line

        return '\n'.join(bill_content)

    def print_to_printer(self, bill_number: str, customer_name: str, bill_items: List[Dict],
                        total_amount: float, date: str, time: str, printer_name: str = None) -> bool:
        """Print bill to physical printer with enhanced error handling"""

        # Check if physical printers are available
        if not self.is_physical_printer_available():
            print("ERROR: No physical printers detected. Please connect a printer and try again.")
            return False

        # Refresh printer list to ensure current status
        self.refresh_printer_list()

        # Determine which printer to use
        target_printer = None
        if printer_name:
            # Use specified printer if available
            for printer in self.physical_printers:
                if printer['name'] == printer_name and printer['online']:
                    target_printer = printer
                    break
        else:
            # Use default printer or first available
            target_printer = self.default_printer or self.physical_printers[0]

        if not target_printer:
            print("ERROR: No suitable printer found for printing.")
            return False

        print(f"Printing to: {target_printer['name']}")

        try:
            if platform.system() == "Windows" and WIN32_AVAILABLE:
                return self._print_windows(bill_number, customer_name, bill_items,
                                         total_amount, date, time, target_printer)
            else:
                return self._print_unix(bill_number, customer_name, bill_items,
                                      total_amount, date, time, target_printer)
        except Exception as e:
            print(f"ERROR: Printing failed: {e}")
            return False

    def _print_windows(self, bill_number: str, customer_name: str, bill_items: List[Dict],
                      total_amount: float, date: str, time: str, printer: Dict) -> bool:
        """Windows-specific printing implementation with Brother printer optimization"""

        # Special handling for Brother printers - use physical print method
        is_brother = 'brother' in printer['name'].lower()

        if is_brother:
            print(f"Detected Brother printer: {printer['name']}")
            print("Using Brother-optimized physical printing method...")

            # Method 1: Windows Notepad print (proven to work physically)
            try:
                bill_content = self.create_bill_content(bill_number, customer_name, bill_items,
                                                       total_amount, date, time)

                # Create temporary file for notepad printing
                temp_file = os.path.join(self.temp_dir, f"bill_{bill_number}_notepad.txt")

                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(bill_content)

                print(f"📝 Created bill file: {temp_file}")

                # Use notepad /p to print (this method actually works!)
                import subprocess
                result = subprocess.run(['notepad', '/p', temp_file], shell=True,
                                      capture_output=True, text=True, timeout=30)

                print(f"🖨️ Notepad print result: {result.returncode}")

                if result.returncode == 0:
                    print("✅ Physical print job sent via Notepad method!")

                    # Wait for printing to complete
                    import time
                    time.sleep(3)

                    # Clean up temp file
                    try:
                        os.remove(temp_file)
                    except:
                        pass

                    return True
                else:
                    print(f"❌ Notepad print failed with code: {result.returncode}")
                    return False

            except Exception as e:
                print(f"❌ Notepad printing failed: {e}")

            # Method 2: Enhanced copy to PRN method (backup for Brother)
            try:
                print("🔄 Trying enhanced copy to PRN method...")

                bill_content = self.create_bill_content(bill_number, customer_name, bill_items,
                                                       total_amount, date, time)

                temp_file = os.path.join(self.temp_dir, f"bill_{bill_number}_prn.txt")

                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(bill_content)

                # Use copy command to PRN
                result = subprocess.run(['copy', temp_file, 'PRN'], shell=True,
                                      capture_output=True, text=True)

                print(f"📋 Copy to PRN result: {result.returncode}")

                if result.returncode == 0 and "copied" in result.stdout.lower():
                    print("✅ Physical print via copy to PRN successful!")

                    # Clean up
                    try:
                        os.remove(temp_file)
                    except:
                        pass

                    return True

            except Exception as e:
                print(f"❌ Copy to PRN failed: {e}")

        # Method 3: Try PDF printing (best quality) for non-Brother or as fallback
        if REPORTLAB_AVAILABLE:
            try:
                temp_pdf = os.path.join(self.temp_dir, f"bill_{bill_number}_temp.pdf")
                pdf_path = self.save_as_pdf(bill_number, customer_name, bill_items,
                                          total_amount, date, time, temp_pdf)

                if pdf_path and os.path.exists(pdf_path):
                    # Use win32api for reliable PDF printing
                    win32api.ShellExecute(0, "print", pdf_path, f'/d:"{printer["name"]}"', ".", 0)

                    # Wait for print job to process
                    import time
                    time.sleep(3)

                    # Verify print job was submitted
                    try:
                        handle = win32print.OpenPrinter(printer['name'])
                        jobs = win32print.EnumJobs(handle, 0, -1, 1)
                        win32print.ClosePrinter(handle)

                        if jobs:
                            print(f"Print job submitted successfully. {len(jobs)} jobs in queue.")
                        else:
                            print("Print job completed or printer queue is empty.")

                    except Exception as e:
                        print(f"Could not check print queue: {e}")

                    # Clean up
                    try:
                        os.remove(pdf_path)
                    except:
                        pass

                    return True
            except Exception as e:
                print(f"PDF printing failed: {e}")

        # Method 4: Standard text printing fallback
        try:
            bill_content = self.create_bill_content(bill_number, customer_name, bill_items,
                                                   total_amount, date, time)

            # Send directly to printer using win32print
            handle = win32print.OpenPrinter(printer['name'])
            try:
                job_id = win32print.StartDocPrinter(handle, 1, ("Bill Print Job", None, "RAW"))
                win32print.StartPagePrinter(handle)
                win32print.WritePrinter(handle, bill_content.encode('utf-8'))
                win32print.EndPagePrinter(handle)
                win32print.EndDocPrinter(handle)
                print(f"Text print job {job_id} submitted successfully.")
                return True
            finally:
                win32print.ClosePrinter(handle)

        except Exception as e:
            print(f"Direct text printing failed: {e}")

        return False

    def _format_for_brother_printer(self, content: str) -> str:
        """Format content specifically for Brother laser printers"""
        lines = content.split('\n')
        formatted_lines = []

        for line in lines:
            # Ensure lines don't exceed Brother's character width (usually 80 chars)
            if len(line) > 80:
                line = line[:80]
            formatted_lines.append(line)

        # Join with proper line endings and add form feed at the end
        formatted_content = '\r\n'.join(formatted_lines)
        formatted_content += '\r\n\f'  # Add carriage return, line feed, and form feed

        return formatted_content

    def _print_unix(self, bill_number: str, customer_name: str, bill_items: List[Dict],
                   total_amount: float, date: str, time: str, printer: Dict) -> bool:
        """Unix/Linux specific printing implementation"""
        try:
            bill_content = self.create_bill_content(bill_number, customer_name, bill_items,
                                                   total_amount, date, time)

            temp_file = os.path.join(self.temp_dir, f"bill_{bill_number}.txt")
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(bill_content)

            # Use lp command to print
            result = subprocess.run(['lp', '-d', printer['name'], temp_file],
                                  capture_output=True, text=True)

            try:
                os.remove(temp_file)
            except:
                pass

            if result.returncode == 0:
                print("Print job submitted successfully on Unix system.")
                return True
            else:
                print(f"Unix printing failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"Unix printing failed: {e}")
            return False

    # Keep existing methods for backward compatibility
    def check_printer_availability(self) -> bool:
        """Legacy method for backward compatibility"""
        return self.is_physical_printer_available()

    def get_default_printer_name(self) -> Optional[str]:
        """Legacy method for backward compatibility"""
        if self.default_printer:
            return self.default_printer['name']
        return None

    # NEW RELIABLE PRINTING METHODS - Simple methods that actually work
    def print_via_notepad(self, bill_number: str, customer_name: str, bill_items: List[Dict],
                         total_amount: float, date: str, time: str) -> bool:
        """Print bill using Windows Notepad method - most reliable physical printing"""
        try:
            print("🖨️ Using reliable Notepad printing method...")

            # Create bill content
            bill_content = self.create_bill_content(bill_number, customer_name, bill_items,
                                                   total_amount, date, time)

            # Create temporary file
            temp_file = os.path.join(self.temp_dir, f"bill_{bill_number}_notepad.txt")

            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(bill_content)

            print(f"📝 Created bill file: {temp_file}")

            # Use notepad /p to print - this method actually works!
            result = subprocess.run(['notepad', '/p', temp_file], shell=True,
                                  capture_output=True, text=True, timeout=30)

            print(f"🖨️ Notepad print result: {result.returncode}")

            if result.returncode == 0:
                print("✅ Physical print job sent via Notepad method!")

                # Wait for printing to complete
                import time
                time.sleep(3)

                # Clean up temp file
                try:
                    os.remove(temp_file)
                except:
                    pass

                return True
            else:
                print(f"❌ Notepad print failed with code: {result.returncode}")
                return False

        except Exception as e:
            print(f"❌ Notepad printing failed: {e}")
            return False

    def print_via_copy_prn(self, bill_number: str, customer_name: str, bill_items: List[Dict],
                          total_amount: float, date: str, time: str) -> bool:
        """Print bill using copy to PRN method - direct printer method"""
        try:
            print("📋 Using direct copy to PRN method...")

            # Create bill content
            bill_content = self.create_bill_content(bill_number, customer_name, bill_items,
                                                   total_amount, date, time)

            # Create temporary file
            temp_file = os.path.join(self.temp_dir, f"bill_{bill_number}_prn.txt")

            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(bill_content)

            print(f"📝 Created bill file: {temp_file}")

            # Use copy command to PRN (default printer)
            result = subprocess.run(['copy', temp_file, 'PRN'], shell=True,
                                  capture_output=True, text=True)

            print(f"📋 Copy to PRN result: {result.returncode}")

            if result.returncode == 0 and "copied" in result.stdout.lower():
                print("✅ Physical print via copy to PRN successful!")

                # Clean up
                try:
                    os.remove(temp_file)
                except:
                    pass

                return True
            else:
                print(f"❌ Copy to PRN failed")
                return False

        except Exception as e:
            print(f"❌ Copy to PRN failed: {e}")
            return False

    def print_or_save_bill(self, bill_number: str, customer_name: str, customer_mobile: str,
                          bill_items: List[Dict], total_amount: float, date: str, time: str) -> tuple:
        """Enhanced print or save method with reliable printing options"""
        print_success = False
        save_success = False
        message = ""

        try:
            # Try reliable printing methods in order of preference
            print("🎯 Attempting reliable physical printing...")

            # Method 1: Try Notepad printing (most reliable)
            if self.print_via_notepad(bill_number, customer_name, bill_items, total_amount, date, time):
                print_success = True
                message += "✅ Printed via Notepad method. "
            else:
                # Method 2: Try copy to PRN as backup
                print("🔄 Notepad failed, trying copy to PRN...")
                if self.print_via_copy_prn(bill_number, customer_name, bill_items, total_amount, date, time):
                    print_success = True
                    message += "✅ Printed via copy to PRN method. "
                else:
                    # Method 3: Try standard printer method as last resort
                    print("🔄 Copy to PRN failed, trying standard method...")
                    if self.print_to_printer(bill_number, customer_name, bill_items, total_amount, date, time):
                        print_success = True
                        message += "✅ Printed via standard method. "
                    else:
                        message += "❌ All printing methods failed. "

            # Always save bill to file
            try:
                bill_content = self.create_bill_content(bill_number, customer_name, bill_items,
                                                       total_amount, date, time)

                # Ensure bills directory exists using correct path
                bills_dir = get_bills_directory()

                # Save as text file
                txt_filename = f"bill_{bill_number}_{date.replace('-', '')}.txt"
                txt_path = get_bill_file_path(bill_number, date.replace('-', ''), 'txt')

                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(bill_content)

                save_success = True
                message += f"💾 Saved as {txt_filename}. "

                # Also try to save as PDF if available
                if REPORTLAB_AVAILABLE:
                    pdf_filename = f"bill_{bill_number}_{date.replace('-', '')}.pdf"
                    pdf_path = get_bill_file_path(bill_number, date.replace('-', ''), 'pdf')

                    if self.save_as_pdf(bill_number, customer_name, bill_items,
                                       total_amount, date, time, pdf_path):
                        message += f"📄 PDF saved as {pdf_filename}. "

            except Exception as e:
                message += f"❌ Save failed: {e} "

        except Exception as e:
            message += f"❌ Print/Save error: {e} "

        return (print_success, save_success, message)

    def save_as_pdf(self, bill_number: str, customer_name: str, bill_items: List[Dict],
                    total_amount: float, date: str, time: str, save_path: str = None) -> str:
        """Save bill as PDF file with professional design"""
        if not REPORTLAB_AVAILABLE:
            print("ReportLab not available, saving as text file")
            return self.save_as_text_file(bill_number, customer_name, bill_items,
                                        total_amount, date, time, save_path)

        try:
            # Create filename and path using correct directory
            if save_path is None:
                save_path = get_bill_file_path(bill_number, date.replace('-', ''), 'pdf')

            # Create PDF with professional styling
            doc = SimpleDocTemplate(save_path, pagesize=A4,
                                  leftMargin=50, rightMargin=50,
                                  topMargin=50, bottomMargin=50)
            styles = getSampleStyleSheet()
            story = []

            # Custom styles for professional look
            from reportlab.lib.styles import ParagraphStyle
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

            # Professional header style
            header_style = ParagraphStyle(
                'CustomHeader',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.black,
                alignment=TA_CENTER,
                spaceAfter=6,
                fontName='Helvetica-Bold'
            )

            # Restaurant info style
            restaurant_style = ParagraphStyle(
                'RestaurantInfo',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.black,
                alignment=TA_CENTER,
                spaceAfter=4,
                fontName='Helvetica'
            )

            # Bill info style
            bill_info_style = ParagraphStyle(
                'BillInfo',
                parent=styles['Normal'],
                fontSize=11,
                textColor=colors.black,
                alignment=TA_LEFT,
                spaceAfter=4,
                fontName='Helvetica'
            )

            # Header with restaurant info
            header = get_bill_header()
            header_lines = header.split('\n')

            # Restaurant name (first line) - larger
            if header_lines:
                restaurant_name = header_lines[0].strip()
                if restaurant_name:
                    p = Paragraph(restaurant_name, header_style)
                    story.append(p)

            # Other header lines (address, phone, etc.)
            for line in header_lines[1:]:
                if line.strip():
                    p = Paragraph(line.strip(), restaurant_style)
                    story.append(p)

            # Add separator line
            story.append(Spacer(1, 12))
            separator_table = Table([['_' * 80]], colWidths=[7*inch])
            separator_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0, colors.white)
            ]))
            story.append(separator_table)
            story.append(Spacer(1, 12))

            # Bill details in professional format
            bill_info_data = [
                [f"Bill Number: {bill_number}", f"Date: {date}"],
                [f"Customer: {customer_name}", f"Time: {time}"]
            ]

            bill_info_table = Table(bill_info_data, colWidths=[3.5*inch, 3.5*inch])
            bill_info_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0, colors.white)
            ]))
            story.append(bill_info_table)
            story.append(Spacer(1, 16))

            # Items table with professional styling
            table_data = [['Item', 'Qty', 'Price', 'Total']]

            # Use Rs instead of rupee symbol to avoid PDF issues
            for item in bill_items:
                table_data.append([
                    item['name'],
                    str(item['quantity']),
                    f"Rs {item['price']:.2f}",
                    f"Rs {item['total']:.2f}"
                ])

            # Add separator row
            table_data.append(['', '', '', ''])

            # Total row
            table_data.append(['', '', 'TOTAL AMOUNT:', f"Rs {total_amount:.2f}"])

            table = Table(table_data, colWidths=[3.5*inch, 0.8*inch, 1.3*inch, 1.4*inch])
            table.setStyle(TableStyle([
                # Header row styling
                ('BACKGROUND', (0, 0), (-1, 0), colors.white),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (0, 1), (0, -3), 'LEFT'),  # Item names left-aligned
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),

                # Data rows styling
                ('BACKGROUND', (0, 1), (-1, -3), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -3), colors.black),
                ('FONTNAME', (0, 1), (-1, -3), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -3), 10),
                ('TOPPADDING', (0, 1), (-1, -3), 4),
                ('BOTTOMPADDING', (0, 1), (-1, -3), 4),

                # Separator row (empty)
                ('BACKGROUND', (0, -2), (-1, -2), colors.white),
                ('LINEBELOW', (0, -3), (-1, -3), 1, colors.black),

                # Total row styling
                ('BACKGROUND', (0, -1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 11),
                ('TOPPADDING', (0, -1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, -1), (-1, -1), 6),
                ('ALIGN', (2, -1), (2, -1), 'RIGHT'),
                ('ALIGN', (3, -1), (3, -1), 'RIGHT'),

                # Borders
                ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),  # Header underline
                ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),  # Total underline
                ('LINEBEFORE', (1, 0), (1, -1), 0.5, colors.lightgrey),  # Vertical separators
                ('LINEBEFORE', (2, 0), (2, -1), 0.5, colors.lightgrey),
                ('LINEBEFORE', (3, 0), (3, -1), 0.5, colors.lightgrey),
            ]))
            story.append(table)
            story.append(Spacer(1, 20))

            # Footer
            footer = get_bill_footer()
            footer_lines = footer.split('\n')
            for line in footer_lines:
                if line.strip():
                    p = Paragraph(line.strip(), restaurant_style)
                    story.append(p)

            # Build the PDF
            doc.build(story)
            print(f"PDF bill saved: {save_path}")
            return save_path

        except Exception as e:
            print(f"PDF generation failed: {e}")
            # Fallback to text file
            return self.save_as_text_file(bill_number, customer_name, bill_items,
                                        total_amount, date, time, save_path)

    def save_as_text_file(self, bill_number: str, customer_name: str, bill_items: List[Dict],
                         total_amount: float, date: str, time: str, save_path: str = None) -> str:
        """Save bill as text file (fallback when PDF is not available)"""
        try:
            # Create filename and path using correct directory
            if save_path is None:
                save_path = get_bill_file_path(bill_number, date.replace('-', ''), 'txt')
            else:
                # Change extension to .txt if it was .pdf
                if save_path.endswith('.pdf'):
                    save_path = save_path.replace('.pdf', '.txt')

            # Create bill content
            bill_content = self.create_bill_content(bill_number, customer_name, bill_items,
                                                   total_amount, date, time)

            # Save to file
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(bill_content)

            print(f"Text bill saved: {save_path}")
            return save_path

        except Exception as e:
            print(f"Failed to save text file: {e}")
            return None

    def diagnose_printer_issues(self):
        """Diagnose common printer connectivity issues"""
        print("\n🔍 PRINTER DIAGNOSTICS")
        print("=" * 50)

        # Check Windows Print Spooler service
        try:
            result = subprocess.run(['sc', 'query', 'spooler'],
                                  capture_output=True, text=True, shell=True)
            if 'RUNNING' in result.stdout:
                print("✅ Print Spooler service is running")
            else:
                print("❌ Print Spooler service is not running")
                print("💡 Try: services.msc -> Start Print Spooler")
        except:
            print("⚠️ Could not check Print Spooler status")

        # Check default printer
        try:
            if WIN32_AVAILABLE:
                default = win32print.GetDefaultPrinter()
                print(f"🖨️ Default printer: {default}")
            else:
                print("⚠️ Cannot check default printer (win32print not available)")
        except:
            print("❌ No default printer set")
            print("💡 Set a default printer in Windows Settings")

        # List all detected printers
        print(f"\n📋 Detected printers: {len(self.physical_printers)}")
        for i, printer in enumerate(self.physical_printers, 1):
            status = "🟢 Online" if printer.get('online') else "🔴 Offline"
            default_mark = " (DEFAULT)" if printer.get('default') else ""
            print(f"  {i}. {printer['name']}{default_mark} - {status}")

        if not self.physical_printers:
            print("❌ No physical printers detected!")
            print("💡 Troubleshooting steps:")
            print("   1. Check printer is powered on")
            print("   2. Check USB/network connection")
            print("   3. Install/update printer drivers")
            print("   4. Restart Print Spooler service")
            print("   5. Add printer in Windows Settings")

# Legacy compatibility function
def create_bill_printer():
    """Create and return an enhanced bill printer instance"""
    return EnhancedBillPrinter()

# For backward compatibility
BillPrinter = EnhancedBillPrinter
