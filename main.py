#!/usr/bin/env python3
"""
Programming Tools Version Checker
A desktop application to check and display versions of programming languages,
package managers, frameworks, and development tools.

Author: Augment Agent
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import ctypes

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from gui import VersionCheckerGUI
except ImportError as e:
    print(f"Error importing GUI module: {e}")
    sys.exit(1)

def is_admin():
    """Check if the current process has administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Restart the current script with administrator privileges."""
    try:
        if is_admin():
            # Already running as admin
            return True
        else:
            # Re-run the program with admin rights
            print("Requesting administrator privileges...")
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                sys.executable,
                " ".join(sys.argv),
                None,
                1
            )
            return False
    except Exception as e:
        print(f"Failed to elevate privileges: {e}")
        return False

def main():
    """Main entry point for the application."""
    try:
        # Check for admin privileges and request if needed
        if not is_admin():
            print("Application requires administrator privileges for full functionality.")
            print("This includes Windows service management, system cleanup, and advanced features.")

            # Try to restart with admin privileges
            if not run_as_admin():
                # Exit current instance - the elevated instance will start
                print("Exiting current instance...")
                sys.exit(0)

        print("Running with administrator privileges.")

        # Check if tkinter is available
        root = tk.Tk()
        root.withdraw()  # Hide the root window temporarily
        root.destroy()  # Destroy the temporary root
        
        # Import the login module
        from login import LoginWindow
        
        # Define a callback function for successful login
        def on_login_success():
            # Create and run the application after successful login
            app = VersionCheckerGUI()
            app.run()
        
        # Show login window first
        login_window = LoginWindow(on_login_success)
        login_window.run()
        
    except tk.TclError as e:
        print(f"GUI Error: {e}")
        print("Make sure you have tkinter installed and a display available.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
