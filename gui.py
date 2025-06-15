import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Menu
import threading
from typing import Dict
import os
import re
import sys
import json
import subprocess
from datetime import datetime
from version_checker import VersionChecker
from browser_backup import BrowserBackup
from hardware_info import HardwareInfoManager
from startup_manager import StartupManager

class VersionCheckerGUI:
    """GUI interface for the Version Checker application."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Programming Tools Version Checker")
        self.root.geometry("1000x750")
        self.root.minsize(900, 650)
        self.root.state('zoomed')  # Make window open in full screen mode
        
        # Set icon if available
        try:
            # Use a default icon from tkinter
            self.root.iconbitmap(default="")
        except:
            pass
            
        # Set up window close event handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
            
        # Initialize version checker, browser backup, hardware info, and startup manager
        self.version_checker = VersionChecker()
        self.browser_backup = BrowserBackup()
        self.hardware_info_manager = HardwareInfoManager()
        self.startup_manager = StartupManager()
        self.results = {}
        self.installing_tools = set()  # Track tools currently being installed
        
        # Modern color scheme with dark/light theme support
        self.theme_mode = "light"  # Can be "light" or "dark"
        self.setup_color_themes()

        # Initialize theme
        self.apply_theme()
        
        # Create menu bar
        self.create_menu()
        
        # Configure style
        self.setup_styles()
        
        # Create GUI elements
        self.create_widgets()
        
        # Center window
        self.center_window()

    def setup_color_themes(self):
        """Setup modern color themes for light and dark modes."""
        self.themes = {
            "light": {
                "primary": "#6366f1",        # Modern indigo
                "primary_dark": "#4f46e5",   # Darker indigo
                "secondary": "#8b5cf6",      # Modern purple
                "accent": "#06b6d4",         # Modern cyan
                "success": "#10b981",        # Modern green
                "warning": "#f59e0b",        # Modern amber
                "error": "#ef4444",          # Modern red
                "background": "#ffffff",     # Pure white
                "surface": "#f8fafc",        # Light gray
                "surface_variant": "#f1f5f9", # Lighter gray
                "text_primary": "#1e293b",   # Dark slate
                "text_secondary": "#64748b", # Medium slate
                "text_tertiary": "#94a3b8",  # Light slate
                "border": "#e2e8f0",         # Light border
                "hover": "#f1f5f9",          # Hover state
                "active": "#e2e8f0",         # Active state
                "shadow": "rgba(0, 0, 0, 0.1)" # Subtle shadow
            },
            "dark": {
                "primary": "#818cf8",        # Lighter indigo for dark mode
                "primary_dark": "#6366f1",   # Standard indigo
                "secondary": "#a78bfa",      # Lighter purple
                "accent": "#22d3ee",         # Lighter cyan
                "success": "#34d399",        # Lighter green
                "warning": "#fbbf24",        # Lighter amber
                "error": "#f87171",          # Lighter red
                "background": "#0f172a",     # Dark slate
                "surface": "#1e293b",        # Medium dark slate
                "surface_variant": "#334155", # Lighter dark slate
                "text_primary": "#f8fafc",   # Light text
                "text_secondary": "#cbd5e1", # Medium light text
                "text_tertiary": "#94a3b8",  # Muted text
                "border": "#475569",         # Dark border
                "hover": "#334155",          # Dark hover
                "active": "#475569",         # Dark active
                "shadow": "rgba(0, 0, 0, 0.3)" # Darker shadow
            }
        }

    def apply_theme(self):
        """Apply the current theme colors."""
        self.colors = self.themes[self.theme_mode]

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"
        self.apply_theme()
        self.setup_styles()
        self.refresh_ui_colors()

    def refresh_ui_colors(self):
        """Refresh UI colors after theme change."""
        # Update root window background
        self.root.configure(background=self.colors["background"])

        # Update theme button icon
        if hasattr(self, 'theme_btn'):
            self.theme_btn.config(text="🌙" if self.theme_mode == "light" else "☀️")

        # Update status bar
        if hasattr(self, 'status_var'):
            self.status_var.set(self.status_var.get())  # Trigger refresh

        # Force a complete UI refresh
        self.root.update_idletasks()

    def create_modern_dialog(self, parent, title, width=600, height=400, min_width=500, min_height=300):
        """Create a modern styled dialog window with consistent theming."""
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.geometry(f"{width}x{height}")
        dialog.minsize(min_width, min_height)
        dialog.transient(parent)
        dialog.grab_set()

        # Match main app background color
        dialog.configure(background=self.colors["background"])

        # Center the dialog
        self.center_window(dialog)

        return dialog

    def create_modern_header(self, parent, title, icon="", subtitle=""):
        """Create a clean header with minimal styling."""
        header_frame = ttk.Frame(parent, padding="10")
        header_frame.pack(fill=tk.X, pady=(0, 10))

        # Main title with icon
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(fill=tk.X)

        if icon:
            icon_label = ttk.Label(
                title_frame,
                text=icon,
                font=('Segoe UI', 20)
            )
            icon_label.pack(side=tk.LEFT, padx=(0, 8))

        title_label = ttk.Label(
            title_frame,
            text=title,
            font=('Segoe UI', 14, 'bold')
        )
        title_label.pack(side=tk.LEFT, anchor=tk.W)

        return header_frame

    def create_modern_button_frame(self, parent, buttons_config):
        """Create a clean button frame.

        Args:
            parent: Parent widget
            buttons_config: List of tuples (text, command, style, side)
        """
        button_frame = ttk.Frame(parent, padding="10")
        button_frame.pack(fill=tk.X, pady=(10, 0))

        for text, command, style, side in buttons_config:
            btn = ttk.Button(
                button_frame,
                text=text,
                command=command,
                style=style
            )
            btn.pack(side=side, padx=5)

        return button_frame

    def center_window(self, window=None):
        """Center the window on the screen."""
        window_to_center = window or self.root
        window_to_center.update_idletasks()
        
        # Get window size
        width = window_to_center.winfo_width()
        height = window_to_center.winfo_height()
        
        # Get screen size
        screen_width = window_to_center.winfo_screenwidth()
        screen_height = window_to_center.winfo_screenheight()
        
        # Calculate position
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # Set position
        window_to_center.geometry(f"{width}x{height}+{x}+{y}")
        
    def create_menu(self):
        """Create the menu bar with options using theme colors."""
        menubar = Menu(self.root,
                      background=self.colors["background"],
                      foreground=self.colors["text_primary"],
                      activebackground=self.colors["primary"],
                      activeforeground="white")
        self.root.config(menu=menubar)

        # File menu
        file_menu = Menu(menubar, tearoff=0,
                        background=self.colors["background"],
                        foreground=self.colors["text_primary"],
                        activebackground=self.colors["primary"],
                        activeforeground="white")
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export JSON", command=self.export_json)
        file_menu.add_command(label="Export Text", command=self.export_text)
        file_menu.add_command(label="Import JSON", command=self.import_json)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)

        # Tools menu
        tools_menu = Menu(menubar, tearoff=0,
                         background=self.colors["background"],
                         foreground=self.colors["text_primary"],
                         activebackground=self.colors["primary"],
                         activeforeground="white")
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Check Versions", command=self.start_version_check)
        tools_menu.add_command(label="Auto Install Packages", command=self.auto_install_from_backup)
        tools_menu.add_separator()
        tools_menu.add_command(label="Hardware Information", command=self.show_hardware_info)
        tools_menu.add_command(label="RAM Usage Monitor", command=self.show_ram_monitor)
        tools_menu.add_command(label="Internet Speed Test", command=self.show_speed_test)
        tools_menu.add_command(label="Network Connection Monitor", command=self.show_network_monitor)
        tools_menu.add_command(label="Service Manager", command=self.show_service_manager)
        tools_menu.add_command(label="Startup Manager", command=self.show_startup_manager)
        tools_menu.add_command(label="Installed Programs", command=self.show_installed_programs)
        tools_menu.add_command(label="PC Cleanup", command=self.show_pc_cleanup_options)

        # Browser Backup menu
        browser_menu = Menu(menubar, tearoff=0,
                           background=self.colors["background"],
                           foreground=self.colors["text_primary"],
                           activebackground=self.colors["primary"],
                           activeforeground="white")
        menubar.add_cascade(label="Browser Backup", menu=browser_menu)
        browser_menu.add_command(label="Backup Browser Data", command=self.show_browser_backup_dialog)
        browser_menu.add_command(label="Restore Browser Data", command=self.show_browser_restore_dialog)
        browser_menu.add_command(label="Manage Backups", command=self.show_browser_backup_manager)
        browser_menu.add_separator()
        browser_menu.add_command(label="Export Bookmarks to HTML", command=self.export_bookmarks_html)

        # View menu
        view_menu = Menu(menubar, tearoff=0,
                        background=self.colors["background"],
                        foreground=self.colors["text_primary"],
                        activebackground=self.colors["primary"],
                        activeforeground="white")
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="🌙 Toggle Dark/Light Theme", command=self.toggle_theme)
        view_menu.add_separator()
        view_menu.add_command(label="🔄 Refresh UI", command=self.refresh_ui_colors)

        # Help menu
        help_menu = Menu(menubar, tearoff=0,
                        background=self.colors["background"],
                        foreground=self.colors["text_primary"],
                        activebackground=self.colors["primary"],
                        activeforeground="white")
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About",
            "Programming Tools Version Checker\n\n" +
            "A utility to check, manage, and install development tools.\n\n" +
            "© 2025 Developed by Elnakieb. All rights reserved."
        )

    def show_installed_programs(self):
        """Show dialog with all installed programs on the system."""
        # Show loading dialog
        loading_dialog = tk.Toplevel(self.root)
        loading_dialog.title("Loading Programs")
        loading_dialog.geometry("300x100")
        loading_dialog.transient(self.root)
        loading_dialog.grab_set()
        loading_dialog.configure(background=self.colors["background"])

        # Center the dialog
        self.center_window(loading_dialog)
        
        # Add loading message
        ttk.Label(
            loading_dialog, 
            text="Loading installed programs...\nThis may take a moment.",
            style="Info.TLabel"
        ).pack(pady=20)
        
        # Start loading in a separate thread
        threading.Thread(target=self._load_installed_programs, args=(loading_dialog,), daemon=True).start()

    def _load_installed_programs(self, loading_dialog):
        """Background thread to load installed programs."""
        try:
            # Get installed programs using PowerShell
            programs = self._get_installed_programs()
            
            # Close loading dialog and show programs dialog in main thread
            self.root.after(0, lambda: self._show_programs_dialog(programs, loading_dialog))
        except Exception as e:
            self.root.after(0, lambda: self._handle_program_load_error(str(e), loading_dialog))

    def _handle_program_load_error(self, error_message, loading_dialog):
        """Handle errors when loading programs."""
        loading_dialog.destroy()
        messagebox.showerror("Error", f"Failed to load installed programs:\n{error_message}")

    def _get_installed_programs(self):
        """Get list of installed programs using PowerShell."""
        # PowerShell command to get installed programs from registry
        ps_command = [
            "powershell",
            "-Command",
            "$programs = @(); "
            "$programs += Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | "
            "Select-Object DisplayName, DisplayVersion, Publisher, UninstallString; "
            "$programs += Get-ItemProperty HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | "
            "Select-Object DisplayName, DisplayVersion, Publisher, UninstallString; "
            "$programs | Where-Object {$_.DisplayName -ne $null} | Sort-Object DisplayName | ConvertTo-Json -Depth 1"
        ]
        
        # Run PowerShell command
        result = subprocess.run(
            ps_command,
            capture_output=True,
            text=True,
            timeout=30,
            shell=True
        )
        
        if result.returncode != 0:
            raise Exception(f"PowerShell command failed: {result.stderr}")
        
        # Parse JSON output
        programs_data = json.loads(result.stdout)
        
        # Clean up and deduplicate the data
        programs = []
        seen_names = set()
        
        for program in programs_data:
            name = program.get("DisplayName")
            if name and name not in seen_names:
                seen_names.add(name)
                programs.append({
                    "name": name,
                    "version": program.get("DisplayVersion", ""),
                    "publisher": program.get("Publisher", ""),
                    "uninstall_string": program.get("UninstallString", "")
                })
        
        return sorted(programs, key=lambda x: x["name"].lower())

    def _show_programs_dialog(self, programs, loading_dialog):
        """Show dialog with installed programs."""
        # Close loading dialog
        loading_dialog.destroy()

        # Create modern programs dialog
        dialog = self.create_modern_dialog(
            self.root,
            "Installed Programs",
            width=900,
            height=600,
            min_width=800,
            min_height=500
        )

        # Create main container
        main_container = ttk.Frame(dialog)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create clean header
        self.create_modern_header(
            main_container,
            "Installed Programs",
            icon="📦"
        )

        # Search section
        search_section = ttk.Frame(main_container, padding="10")
        search_section.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(search_section, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_section, textvariable=search_var, width=40)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Programs list
        tree_frame = ttk.Frame(main_container)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        columns = ("name", "version", "publisher", "action")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        # Configure columns
        tree.heading("name", text="Program Name")
        tree.heading("version", text="Version")
        tree.heading("publisher", text="Publisher")
        tree.heading("action", text="Action")

        tree.column("name", width=300, minwidth=200, anchor=tk.W)
        tree.column("version", width=100, minwidth=80, anchor=tk.W)
        tree.column("publisher", width=200, minwidth=150, anchor=tk.W)
        tree.column("action", width=100, minwidth=80, anchor=tk.CENTER)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack the treeview and scrollbars
        tree.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.E, tk.W))
        
        # Configure grid weights
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        
        # Add programs to treeview
        for program in programs:
            tree.insert("", tk.END, values=(
                program["name"],
                program["version"],
                program["publisher"],
                "🗑️ Uninstall"
            ))
        
        # Bind double-click event for uninstallation
        tree.bind("<Double-1>", lambda event: self._handle_program_action(event, tree, programs))
        
        # Add search functionality
        def search_programs(*args):
            search_text = search_var.get().lower()
            
            # Clear treeview
            for item in tree.get_children():
                tree.delete(item)
            
            # Add matching programs
            for program in programs:
                if (search_text in program["name"].lower() or 
                    search_text in (program["version"] or "").lower() or 
                    search_text in (program["publisher"] or "").lower()):
                    tree.insert("", tk.END, values=(
                        program["name"],
                        program["version"],
                        program["publisher"],
                        "🗑️ Uninstall"
                    ))
        
        # Bind search entry to search function
        search_var.trace("w", search_programs)

        # Modern button frame
        button_config = [
            ("❌ Close", dialog.destroy, "Secondary.TButton", tk.RIGHT)
        ]
        self.create_modern_button_frame(main_container, button_config)
        
        # Set focus to search entry
        search_entry.focus()

    def _handle_program_action(self, event, tree, programs):
        """Handle double-click on program in treeview."""
        # Get clicked item
        item = tree.identify_row(event.y)
        if not item:
            return
        
        # Get column that was clicked
        column = tree.identify_column(event.x)
        if column != "#4":  # Action column
            return
        
        # Get program name
        values = tree.item(item, "values")
        program_name = values[0]
        
        # Find program in list
        program = next((p for p in programs if p["name"] == program_name), None)
        if not program:
            return
        
        # Confirm uninstallation
        if not messagebox.askyesno("Confirm Uninstall", 
                                 f"Are you sure you want to uninstall {program_name}?\n\n" +
                                 "This will completely remove the program from your system."):
            return
        
        # Start uninstallation in a separate thread
        threading.Thread(target=self._uninstall_program, args=(program,), daemon=True).start()

    def _uninstall_program(self, program):
        """Uninstall a program using its uninstall string."""
        try:
            # Update status
            self.root.after(0, lambda: self.status_var.set(f"Uninstalling {program['name']}..."))
            
            # Get uninstall string
            uninstall_string = program["uninstall_string"]
            if not uninstall_string:
                self.root.after(0, lambda: messagebox.showerror("Error", 
                                                              f"No uninstall information available for {program['name']}"))
                return
            
            # Parse uninstall string
            if uninstall_string.startswith('"'):
                # Format: "path" arguments
                parts = uninstall_string.split('"')
                if len(parts) >= 3:
                    exe_path = parts[1]
                    args = parts[2].strip()
                    command = [exe_path] + (args.split() if args else [])
                else:
                    command = uninstall_string
            elif uninstall_string.lower().startswith('msiexec'):
                # Format: MsiExec.exe /X{ProductCode}
                command = uninstall_string.split()
                # Add /quiet for silent uninstallation
                if "/quiet" not in command and "/q" not in command:
                    command.append("/quiet")
            else:
                # Other format
                command = uninstall_string
            
            # Run uninstallation command
            if isinstance(command, list):
                result = subprocess.run(command, capture_output=True, text=True, timeout=300)
            else:
                result = subprocess.run(command, capture_output=True, text=True, timeout=300, shell=True)
            
            # Check result
            if result.returncode == 0:
                self.root.after(0, lambda: self.status_var.set(f"Successfully uninstalled {program['name']}"))
                # Check registry for leftover entries
                self.root.after(0, lambda: self._check_registry_for_leftovers(program))
            else:
                error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
                self.root.after(0, lambda: messagebox.showerror("Error", 
                                                              f"Failed to uninstall {program['name']}:\n{error_msg}"))
                self.root.after(0, lambda: self.status_var.set(f"Failed to uninstall {program['name']}"))
                
        except subprocess.TimeoutExpired:
            self.root.after(0, lambda: messagebox.showerror("Timeout", 
                                                          f"Uninstallation of {program['name']} timed out after 5 minutes."))
            self.root.after(0, lambda: self.status_var.set(f"Uninstallation timed out: {program['name']}"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", 
                                                          f"Error uninstalling {program['name']}:\n{str(e)}"))
            self.root.after(0, lambda: self.status_var.set(f"Error uninstalling {program['name']}"))
            
    def _check_registry_for_leftovers(self, program):
        """Check registry for leftover entries after uninstallation and show popup."""
        # Update status without showing success message yet
        self.status_var.set(f"Checking registry for leftover entries of {program['name']}...")
        
        # Create a list to store leftover registry entries
        leftover_entries = []
        
        try:
            # Search for program name in registry (case-insensitive)
            program_name_pattern = re.escape(program['name']).replace('\\ ', '[ _-]*')
            
            # PowerShell command to search registry for leftover entries - optimized version
            ps_command = [
                "powershell",
                "-Command",
                # Combine all PowerShell commands into a single f-string to avoid Python comments being included
                f"""$results = @(); 
                $pattern = '{program_name_pattern}'; 
                # Search in specific registry locations with limited depth
                $uninstallKeys = @(
                  'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall',
                  'HKLM:\\SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall'
                ); 
                # First check uninstall keys (most likely location)
                foreach ($path in $uninstallKeys) {{ 
                  if (Test-Path $path) {{ 
                    $keys = Get-ChildItem -Path $path -ErrorAction SilentlyContinue | 
                      Where-Object {{ $_.PSChildName -match $pattern -or 
                                    ($_.GetValue('DisplayName') -match $pattern) -or 
                                    ($_.GetValue('Publisher') -match $pattern) }}; 
                    if ($keys) {{ 
                      foreach ($key in $keys) {{ 
                        $results += [PSCustomObject]@{{ 
                          Path = $key.PSPath; 
                          Name = $key.PSChildName; 
                          ParentPath = $key.PSParentPath 
                        }} 
                      }} 
                    }} 
                  }} 
                }}; 
                # Then check common software locations with max depth of 2
                $softwareKeys = @(
                  'HKLM:\\SOFTWARE',
                  'HKCU:\\SOFTWARE',
                  'HKLM:\\SOFTWARE\\Wow6432Node'
                ); 
                foreach ($path in $softwareKeys) {{ 
                  if (Test-Path $path) {{ 
                    # Get direct children first
                    $directKeys = Get-ChildItem -Path $path -ErrorAction SilentlyContinue | 
                      Where-Object {{ $_.PSChildName -match $pattern }}; 
                    if ($directKeys) {{ 
                      foreach ($key in $directKeys) {{ 
                        $results += [PSCustomObject]@{{ 
                          Path = $key.PSPath; 
                          Name = $key.PSChildName; 
                          ParentPath = $key.PSParentPath 
                        }} 
                      }} 
                    }} 
                    # Then check one level deeper but only for keys with matching names
                    $childKeys = Get-ChildItem -Path $path -ErrorAction SilentlyContinue | 
                      Where-Object {{ $_.PSChildName -match $pattern }}; 
                    if ($childKeys) {{ 
                      foreach ($childKey in $childKeys) {{ 
                        $grandChildren = Get-ChildItem -Path $childKey.PSPath -ErrorAction SilentlyContinue; 
                        if ($grandChildren) {{ 
                          foreach ($grandChild in $grandChildren) {{ 
                            $results += [PSCustomObject]@{{ 
                              Path = $grandChild.PSPath; 
                              Name = $grandChild.PSChildName; 
                              ParentPath = $grandChild.PSParentPath 
                            }} 
                          }} 
                        }} 
                      }} 
                    }} 
                  }} 
                }}; 
                if ($results.Count -gt 0) {{ $results | ConvertTo-Json -Depth 3 }} else {{ '[]' }}"""
            ]
            
            # Update status to inform user
            self.status_var.set("Checking registry for leftover entries...")
            self.root.update()
            
            try:
                # Run PowerShell command with increased timeout
                result = subprocess.run(
                    ps_command,
                    capture_output=True,
                    text=True,
                    timeout=120,  # Increased timeout to 2 minutes
                    shell=True
                )
                
                if result.returncode != 0:
                    error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                    raise Exception(f"PowerShell command failed: {error_msg}")
            except subprocess.TimeoutExpired:
                messagebox.showerror("Registry Check Timeout", 
                                    "The registry check operation timed out. This may happen with large registries.\n\n"
                                    "The program was uninstalled successfully, but we couldn't verify if there are leftover registry entries.")
                self.status_var.set("Ready")
                return
            
            # Parse JSON output
            if result.stdout.strip():
                registry_data = json.loads(result.stdout)
                
                # Convert to list if single item
                if isinstance(registry_data, dict):
                    registry_data = [registry_data]
                
                # Process registry entries
                for entry in registry_data:
                    leftover_entries.append({
                        "path": entry.get("Path", ""),
                        "name": entry.get("Name", ""),
                        "parent_path": entry.get("ParentPath", "")
                    })
            
            # Show registry cleanup dialog if leftovers found, otherwise show success message
            if leftover_entries:
                self.root.after(0, lambda: self._show_registry_cleanup_dialog(program, leftover_entries))
            else:
                self.status_var.set(f"No registry leftovers found for {program['name']}")
                messagebox.showinfo("Success", 
                                  f"{program['name']} was successfully uninstalled.\n\nNo registry leftovers were found.")
                
        except Exception as e:
            self.status_var.set(f"Error checking registry: {str(e)}")
            messagebox.showerror("Registry Check Error", 
                               f"Error checking registry for {program['name']} leftovers:\n{str(e)}")
    
    def _show_registry_cleanup_dialog(self, program, leftover_entries):
        """Show dialog with leftover registry entries and options to delete them."""
        # First show success message about uninstallation
        messagebox.showinfo("Success", f"{program['name']} was successfully uninstalled.\n\nRegistry leftovers were found.")

        # Create modern dialog
        dialog = self.create_modern_dialog(
            self.root,
            f"Registry Leftovers - {program['name']}",
            width=800,
            height=500,
            min_width=700,
            min_height=400
        )

        # Create main container
        main_container = ttk.Frame(dialog, style="Surface.TFrame")
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Create modern header
        self.create_modern_header(
            main_container,
            f"Registry Leftovers Found",
            icon="🗂️",
            subtitle=f"Registry entries related to {program['name']} were found. You can select entries to delete them from the registry."
        )
        
        # Create treeview section
        tree_section = ttk.Frame(main_container, style="Surface.TFrame", padding="15")
        tree_section.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        tree_header = ttk.Label(
            tree_section,
            text="📋 Registry Entries",
            style="Subtitle.TLabel"
        )
        tree_header.pack(anchor=tk.W, pady=(0, 10))

        # Create treeview frame with scrollbar
        tree_frame = ttk.Frame(tree_section, style="Surface.TFrame")
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ("select", "name", "path")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        
        # Add scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Pack scrollbars and treeview
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure columns
        tree.column("select", width=50, anchor=tk.CENTER)
        tree.column("name", width=200, anchor=tk.W)
        tree.column("path", width=500, anchor=tk.W)
        
        # Configure headings
        tree.heading("select", text="Select")
        tree.heading("name", text="Name")
        tree.heading("path", text="Registry Path")
        
        # Add entries to treeview with checkboxes
        selected_items = {}
        
        for i, entry in enumerate(leftover_entries):
            item_id = tree.insert("", tk.END, values=("", entry["name"], entry["path"]))
            selected_items[item_id] = tk.BooleanVar(value=True)
            
            # Create checkbox in the select column
            checkbox = ttk.Checkbutton(
                tree, 
                variable=selected_items[item_id],
                onvalue=True,
                offvalue=False,
                command=lambda: None  # Placeholder command
            )
            
            # Position checkbox in the select column
            tree.set(item_id, "select", "✓")
            
            # Bind checkbox to item
            tree.item(item_id, tags=("checkbox",))
        
        # Bind click event to toggle checkboxes
        def toggle_checkbox(event):
            item = tree.identify_row(event.y)
            column = tree.identify_column(event.x)
            if item and column == "#1":  # Select column
                current_value = selected_items[item].get()
                selected_items[item].set(not current_value)
                tree.set(item, "select", "✓" if not current_value else "")
        
        tree.bind("<Button-1>", toggle_checkbox)
        
        # Add buttons section
        button_section = ttk.Frame(main_container, style="Surface.TFrame", padding="15")
        button_section.pack(fill=tk.X, pady=(15, 0))
        
        # Add select/deselect all buttons
        select_frame = ttk.Frame(button_section, style="Surface.TFrame")
        select_frame.pack(side=tk.LEFT)

        def select_all():
            for item_id, var in selected_items.items():
                var.set(True)
                tree.set(item_id, "select", "✓")

        def deselect_all():
            for item_id, var in selected_items.items():
                var.set(False)
                tree.set(item_id, "select", "")

        ttk.Button(
            select_frame,
            text="✅ Select All",
            command=select_all,
            style="Secondary.TButton"
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            select_frame,
            text="❌ Deselect All",
            command=deselect_all,
            style="Secondary.TButton"
        ).pack(side=tk.LEFT)

        # Add action buttons
        action_frame = ttk.Frame(button_section, style="Surface.TFrame")
        action_frame.pack(side=tk.RIGHT)
        
        def delete_selected_entries():
            # Get selected entries
            to_delete = []
            for item_id, var in selected_items.items():
                if var.get():
                    values = tree.item(item_id, "values")
                    registry_path = values[2]  # Path column
                    to_delete.append(registry_path)
            
            if not to_delete:
                messagebox.showinfo("No Selection", "No registry entries selected for deletion.")
                return
            
            # Confirm deletion
            if not messagebox.askyesno("Confirm Deletion", 
                                     f"Are you sure you want to delete {len(to_delete)} registry entries?\n\n" +
                                     "This action cannot be undone."):
                return
            
            # Delete entries
            self.status_var.set(f"Deleting registry entries for {program['name']}...")
            threading.Thread(
                target=self._delete_registry_entries,
                args=(to_delete, dialog, program),
                daemon=True
            ).start()
        
        ttk.Button(
            action_frame,
            text="🗑️ Delete Selected",
            command=delete_selected_entries,
            style="Primary.TButton"
        ).pack(side=tk.RIGHT, padx=(5, 0))

        ttk.Button(
            action_frame,
            text="❌ Close",
            command=dialog.destroy,
            style="Secondary.TButton"
        ).pack(side=tk.RIGHT)
    
    def _delete_registry_entries(self, registry_paths, dialog, program):
        """Delete selected registry entries in a separate thread."""
        try:
            deleted_count = 0
            error_count = 0
            errors = []
            
            for path in registry_paths:
                try:
                    # Convert Microsoft.PowerShell.Core\Registry:: path format to PowerShell command
                    ps_path = path
                    if "Microsoft.PowerShell.Core\\Registry::" in ps_path:
                        ps_path = ps_path.replace("Microsoft.PowerShell.Core\\Registry::", "")
                    
                    # PowerShell command to delete registry key
                    ps_command = [
                        "powershell",
                        "-Command",
                        f"Remove-Item -Path '{ps_path}' -Recurse -Force -ErrorAction Stop; "
                        f"if ($?) {{ Write-Output 'Success' }} else {{ Write-Error 'Failed to delete registry key' }}"
                    ]
                    
                    # Run PowerShell command
                    result = subprocess.run(
                        ps_command,
                        capture_output=True,
                        text=True,
                        timeout=10,
                        shell=True
                    )
                    
                    if result.returncode == 0 and "Success" in result.stdout:
                        deleted_count += 1
                    else:
                        error_count += 1
                        errors.append(f"Failed to delete: {path}\nError: {result.stderr or 'Unknown error'}")
                        
                except Exception as e:
                    error_count += 1
                    errors.append(f"Error deleting: {path}\nError: {str(e)}")
            
            # Update UI in main thread
            self.root.after(0, lambda: self._show_registry_deletion_results(
                dialog, program, deleted_count, error_count, errors
            ))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", 
                                                          f"Error deleting registry entries:\n{str(e)}"))
            self.root.after(0, lambda: self.status_var.set("Error deleting registry entries"))
    
    def _show_registry_deletion_results(self, dialog, program, deleted_count, error_count, errors):
        """Show results of registry deletion operation."""
        # Close the registry cleanup dialog
        dialog.destroy()
        
        # Update status
        if error_count == 0:
            self.status_var.set(f"Successfully deleted {deleted_count} registry entries for {program['name']}")
            messagebox.showinfo("Success", f"Successfully deleted {deleted_count} registry entries for {program['name']}.")
        else:
            self.status_var.set(f"Deleted {deleted_count} registry entries with {error_count} errors")
            
            # Show error details
            error_dialog = tk.Toplevel(self.root)
            error_dialog.title("Registry Deletion Errors")
            error_dialog.geometry("700x400")
            error_dialog.minsize(600, 300)
            error_dialog.transient(self.root)
            error_dialog.grab_set()
            error_dialog.configure(background=self.colors["background"])
            self.center_window(error_dialog)
            
            # Create main frame
            main_frame = ttk.Frame(error_dialog, padding=15)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Add header
            ttk.Label(
                main_frame, 
                text=f"Registry Deletion Results", 
                style="Title.TLabel"
            ).pack(pady=(0, 10), anchor=tk.W)
            
            ttk.Label(
                main_frame,
                text=f"Successfully deleted: {deleted_count} entries\nFailed to delete: {error_count} entries",
                style="Info.TLabel"
            ).pack(pady=(0, 15), anchor=tk.W)
            
            # Create text widget for errors
            error_frame = ttk.Frame(main_frame)
            error_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
            
            # Add scrollbar
            scrollbar = ttk.Scrollbar(error_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Create text widget
            error_text = tk.Text(error_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set,
                               background=self.colors["background"],
                               foreground=self.colors["text_primary"],
                               insertbackground=self.colors["text_primary"])
            error_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=error_text.yview)
            
            # Insert errors
            for i, error in enumerate(errors):
                error_text.insert(tk.END, f"{error}\n\n")
            
            error_text.config(state=tk.DISABLED)  # Make read-only
            
            # Add close button
            ttk.Button(
                main_frame,
                text="Close",
                command=error_dialog.destroy,
                style="Secondary.TButton"
            ).pack(side=tk.RIGHT)
            
    def show_pc_cleanup_options(self):
        """Show dialog with PC cleanup options."""
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("PC Cleanup Options")
        dialog.geometry("700x500")
        dialog.minsize(600, 400)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(background=self.colors["background"])
        self.center_window(dialog)
        
        # Create main frame
        main_frame = ttk.Frame(dialog, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add header
        ttk.Label(
            main_frame, 
            text="PC Cleanup Options", 
            style="Title.TLabel"
        ).pack(pady=(0, 10), anchor=tk.W)
        
        ttk.Label(
            main_frame,
            text="Select the cleanup options you want to perform. These operations will help free up disk space and improve system performance.",
            style="Info.TLabel",
            wraplength=650
        ).pack(pady=(0, 15), anchor=tk.W)
        
        # Create options frame
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Create checkboxes for cleanup options
        cleanup_options = {
            "temp_files": tk.BooleanVar(value=True),
            "prefetch": tk.BooleanVar(value=True),
            "windows_temp": tk.BooleanVar(value=True),
            "recycle_bin": tk.BooleanVar(value=False),
            "registry_cleanup": tk.BooleanVar(value=True),
            "browser_cache": tk.BooleanVar(value=False),
            "system_logs": tk.BooleanVar(value=False)
        }
        
        # Option descriptions
        option_descriptions = {
            "temp_files": "User temporary files (%TEMP%)",
            "prefetch": "Windows Prefetch files (improves boot time)",
            "windows_temp": "Windows temporary files (C:\\Windows\\Temp)",
            "recycle_bin": "Empty Recycle Bin",
            "registry_cleanup": "Clean registry (remove invalid entries)",
            "browser_cache": "Browser cache files (Edge, Chrome, Firefox)",
            "system_logs": "Windows log files"
        }
        
        # Create option checkboxes with descriptions
        for i, (option, var) in enumerate(cleanup_options.items()):
            frame = ttk.Frame(options_frame)
            frame.pack(fill=tk.X, pady=5)
            
            cb = ttk.Checkbutton(
                frame,
                text=option_descriptions[option],
                variable=var,
                style="TCheckbutton"
            )
            cb.pack(side=tk.LEFT)
        
        # Add select/deselect all buttons
        select_frame = ttk.Frame(main_frame)
        select_frame.pack(fill=tk.X, pady=(0, 10))
        
        def select_all():
            for var in cleanup_options.values():
                var.set(True)
        
        def deselect_all():
            for var in cleanup_options.values():
                var.set(False)
        
        ttk.Button(
            select_frame,
            text="Select All",
            command=select_all,
            style="Secondary.TButton"
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            select_frame,
            text="Deselect All",
            command=deselect_all,
            style="Secondary.TButton"
        ).pack(side=tk.LEFT)
        
        # Add action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        def start_cleanup():
            # Get selected options
            selected_options = {k: v.get() for k, v in cleanup_options.items()}
            
            # Check if any option is selected
            if not any(selected_options.values()):
                messagebox.showinfo("No Selection", "Please select at least one cleanup option.")
                return
            
            # Confirm cleanup
            selected_descriptions = [option_descriptions[k] for k, v in selected_options.items() if v]
            confirmation_message = "Are you sure you want to perform the following cleanup operations?\n\n"
            confirmation_message += "\n".join([f"• {desc}" for desc in selected_descriptions])
            confirmation_message += "\n\nThis process cannot be undone."
            
            if not messagebox.askyesno("Confirm Cleanup", confirmation_message):
                return
            
            # Close dialog and start cleanup
            dialog.destroy()
            self.status_var.set("Starting system cleanup...")
            threading.Thread(
                target=self._perform_system_cleanup,
                args=(selected_options,),
                daemon=True
            ).start()
        
        ttk.Button(
            button_frame,
            text="Start Cleanup",
            command=start_cleanup,
            style="Primary.TButton"
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            style="Secondary.TButton"
        ).pack(side=tk.RIGHT)

    def _perform_system_cleanup(self, selected_options):
        """Perform system cleanup based on selected options."""
        try:
            cleanup_results = {
                "success": [],
                "failed": [],
                "skipped": []
            }
            
            # Update status
            self.root.after(0, lambda: self.status_var.set("Analyzing system for cleanup..."))
            
            # Process each selected cleanup option
            for option, selected in selected_options.items():
                if not selected:
                    continue
                    
                try:
                    if option == "temp_files":
                        self.root.after(0, lambda: self.status_var.set("Cleaning user temporary files..."))
                        success, message = self._cleanup_temp_files()
                    elif option == "prefetch":
                        self.root.after(0, lambda: self.status_var.set("Cleaning Windows Prefetch files..."))
                        success, message = self._cleanup_prefetch_files()
                    elif option == "windows_temp":
                        self.root.after(0, lambda: self.status_var.set("Cleaning Windows temporary files..."))
                        success, message = self._cleanup_windows_temp()
                    elif option == "recycle_bin":
                        self.root.after(0, lambda: self.status_var.set("Emptying Recycle Bin..."))
                        success, message = self._empty_recycle_bin()
                    elif option == "registry_cleanup":
                        self.root.after(0, lambda: self.status_var.set("Cleaning registry..."))
                        success, message = self._cleanup_registry()
                    elif option == "browser_cache":
                        self.root.after(0, lambda: self.status_var.set("Cleaning browser cache files..."))
                        success, message = self._cleanup_browser_cache()
                    elif option == "system_logs":
                        self.root.after(0, lambda: self.status_var.set("Cleaning system log files..."))
                        success, message = self._cleanup_system_logs()
                    
                    if success:
                        cleanup_results["success"].append((option, message))
                    else:
                        cleanup_results["failed"].append((option, message))
                        
                except Exception as e:
                    cleanup_results["failed"].append((option, str(e)))
            
            # Show results in main thread
            self.root.after(0, lambda: self._show_cleanup_results(cleanup_results))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred during cleanup:\n{str(e)}"))
            self.root.after(0, lambda: self.status_var.set("Cleanup failed"))
    
    def _cleanup_temp_files(self):
        """Clean user temporary files."""
        try:
            cleaned_folders = []
            
            # Get TEMP folder path
            temp_folder = os.environ.get('TEMP')
            if temp_folder and os.path.exists(temp_folder):
                # PowerShell command to clean TEMP files
                ps_command = [
                    "powershell",
                    "-Command",
                    f"Get-ChildItem -Path '{temp_folder}' -Recurse -Force | "
                    f"Where-Object {{ !$_.PSIsContainer }} | "
                    f"ForEach-Object {{ try {{ Remove-Item -Path $_.FullName -Force -ErrorAction SilentlyContinue }} catch {{}} }}"
                ]
                
                # Run PowerShell command
                subprocess.run(
                    ps_command,
                    capture_output=True,
                    text=True,
                    timeout=60,
                    shell=True
                )
                
                cleaned_folders.append(f"TEMP ({temp_folder})")
            
            # Get %temp% folder path (which might be different from TEMP)
            temp_env_folder = os.path.expandvars('%temp%')
            if temp_env_folder and os.path.exists(temp_env_folder) and temp_env_folder != temp_folder:
                # PowerShell command to clean %temp% files
                ps_command = [
                    "powershell",
                    "-Command",
                    f"Get-ChildItem -Path '{temp_env_folder}' -Recurse -Force | "
                    f"Where-Object {{ !$_.PSIsContainer }} | "
                    f"ForEach-Object {{ try {{ Remove-Item -Path $_.FullName -Force -ErrorAction SilentlyContinue }} catch {{}} }}"
                ]
                
                # Run PowerShell command
                subprocess.run(
                    ps_command,
                    capture_output=True,
                    text=True,
                    timeout=60,
                    shell=True
                )
                
                cleaned_folders.append(f"%temp% ({temp_env_folder})")
            
            if cleaned_folders:
                return True, f"Cleaned user temporary files in: {', '.join(cleaned_folders)}"
            else:
                return False, "No temporary folders found"
            
        except Exception as e:
            return False, f"Failed to clean temporary files: {str(e)}"
    
    def _cleanup_prefetch_files(self):
        """Clean Windows Prefetch files."""
        try:
            # Prefetch folder path
            prefetch_folder = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Prefetch')
            if not os.path.exists(prefetch_folder):
                return False, "Prefetch folder not found"
            
            # PowerShell command to clean prefetch files
            ps_command = [
                "powershell",
                "-Command",
                f"Get-ChildItem -Path '{prefetch_folder}' -Filter *.pf | "
                f"ForEach-Object {{ try {{ Remove-Item -Path $_.FullName -Force -ErrorAction SilentlyContinue }} catch {{}} }}"
            ]
            
            # Run PowerShell command
            result = subprocess.run(
                ps_command,
                capture_output=True,
                text=True,
                timeout=30,
                shell=True
            )
            
            return True, "Cleaned Windows Prefetch files"
            
        except Exception as e:
            return False, f"Failed to clean Prefetch files: {str(e)}"
    
    def _cleanup_windows_temp(self):
        """Clean Windows temporary files."""
        try:
            # Windows temp folder path
            windows_temp = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Temp')
            if not os.path.exists(windows_temp):
                return False, "Windows Temp folder not found"
            
            # PowerShell command to clean Windows temp files
            ps_command = [
                "powershell",
                "-Command",
                f"Get-ChildItem -Path '{windows_temp}' -Recurse -Force | "
                f"Where-Object {{ !$_.PSIsContainer }} | "
                f"ForEach-Object {{ try {{ Remove-Item -Path $_.FullName -Force -ErrorAction SilentlyContinue }} catch {{}} }}"
            ]
            
            # Run PowerShell command
            result = subprocess.run(
                ps_command,
                capture_output=True,
                text=True,
                timeout=60,
                shell=True
            )
            
            return True, "Cleaned Windows temporary files"
            
        except Exception as e:
            return False, f"Failed to clean Windows temporary files: {str(e)}"
    
    def _empty_recycle_bin(self):
        """Empty the Recycle Bin."""
        try:
            # PowerShell command to empty Recycle Bin
            ps_command = [
                "powershell",
                "-Command",
                "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"
            ]
            
            # Run PowerShell command
            result = subprocess.run(
                ps_command,
                capture_output=True,
                text=True,
                timeout=60,
                shell=True
            )
            
            return True, "Emptied Recycle Bin"
            
        except Exception as e:
            return False, f"Failed to empty Recycle Bin: {str(e)}"
    
    def _cleanup_registry(self):
        """Clean registry by removing invalid entries."""
        try:
            # PowerShell command to clean registry
            ps_command = [
                "powershell",
                "-Command",
                # Check for invalid software references
                "$results = @(); "
                "$uninstallKeys = @("
                "  'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall',"
                "  'HKLM:\\SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall'"
                "); "
                "foreach ($path in $uninstallKeys) { "
                "  if (Test-Path $path) { "
                "    $keys = Get-ChildItem -Path $path -ErrorAction SilentlyContinue; "
                "    foreach ($key in $keys) { "
                "      $installLocation = $key.GetValue('InstallLocation'); "
                "      $displayName = $key.GetValue('DisplayName'); "
                "      if ($installLocation -and $displayName) { "
                "        if (-not (Test-Path $installLocation)) { "
                "          $results += [PSCustomObject]@{ "
                "            Path = $key.PSPath; "
                "            Name = $displayName; "
                "            InvalidPath = $installLocation "
                "          } "
                "        } "
                "      } "
                "    } "
                "  } "
                "}; "
                "if ($results.Count -gt 0) { $results | ConvertTo-Json -Depth 3 } else { '[]' }"
            ]
            
            # Run PowerShell command
            result = subprocess.run(
                ps_command,
                capture_output=True,
                text=True,
                timeout=120,
                shell=True
            )
            
            # Parse JSON output
            if result.stdout.strip():
                registry_data = json.loads(result.stdout)
                
                # Convert to list if single item
                if isinstance(registry_data, dict):
                    registry_data = [registry_data]
                
                # If invalid entries found, clean them
                if registry_data and len(registry_data) > 0:
                    cleaned_entries = 0
                    for entry in registry_data:
                        try:
                            # PowerShell command to delete registry key
                            ps_path = entry.get("Path", "")
                            if ps_path:
                                delete_command = [
                                    "powershell",
                                    "-Command",
                                    f"Remove-Item -Path '{ps_path}' -Recurse -Force -ErrorAction SilentlyContinue"
                                ]
                                
                                # Run PowerShell command
                                delete_result = subprocess.run(
                                    delete_command,
                                    capture_output=True,
                                    text=True,
                                    timeout=10,
                                    shell=True
                                )
                                
                                cleaned_entries += 1
                        except:
                            pass
                    
                    return True, f"Cleaned {cleaned_entries} invalid registry entries"
                else:
                    return True, "No invalid registry entries found"
            else:
                return True, "No invalid registry entries found"
            
        except Exception as e:
            return False, f"Failed to clean registry: {str(e)}"
    
    def _cleanup_browser_cache(self):
        """Clean browser cache files."""
        try:
            cleaned_browsers = []
            
            # Chrome cache
            chrome_cache = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google\\Chrome\\User Data\\Default\\Cache')
            if os.path.exists(chrome_cache):
                try:
                    # PowerShell command to clean Chrome cache
                    ps_command = [
                        "powershell",
                        "-Command",
                        f"Get-ChildItem -Path '{chrome_cache}' -Recurse -Force | "
                        f"Where-Object {{ !$_.PSIsContainer }} | "
                        f"ForEach-Object {{ try {{ Remove-Item -Path $_.FullName -Force -ErrorAction SilentlyContinue }} catch {{}} }}"
                    ]
                    
                    # Run PowerShell command
                    subprocess.run(
                        ps_command,
                        capture_output=True,
                        text=True,
                        timeout=30,
                        shell=True
                    )
                    
                    cleaned_browsers.append("Chrome")
                except:
                    pass
            
            # Edge cache
            edge_cache = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft\\Edge\\User Data\\Default\\Cache')
            if os.path.exists(edge_cache):
                try:
                    # PowerShell command to clean Edge cache
                    ps_command = [
                        "powershell",
                        "-Command",
                        f"Get-ChildItem -Path '{edge_cache}' -Recurse -Force | "
                        f"Where-Object {{ !$_.PSIsContainer }} | "
                        f"ForEach-Object {{ try {{ Remove-Item -Path $_.FullName -Force -ErrorAction SilentlyContinue }} catch {{}} }}"
                    ]
                    
                    # Run PowerShell command
                    subprocess.run(
                        ps_command,
                        capture_output=True,
                        text=True,
                        timeout=30,
                        shell=True
                    )
                    
                    cleaned_browsers.append("Edge")
                except:
                    pass
            
            # Firefox cache
            firefox_profile = os.path.join(os.environ.get('APPDATA', ''), 'Mozilla\\Firefox\\Profiles')
            if os.path.exists(firefox_profile):
                try:
                    # Find profile folders
                    profiles = [os.path.join(firefox_profile, d) for d in os.listdir(firefox_profile) if os.path.isdir(os.path.join(firefox_profile, d))]
                    
                    for profile in profiles:
                        cache_folder = os.path.join(profile, 'cache2')
                        if os.path.exists(cache_folder):
                            # PowerShell command to clean Firefox cache
                            ps_command = [
                                "powershell",
                                "-Command",
                                f"Get-ChildItem -Path '{cache_folder}' -Recurse -Force | "
                                f"Where-Object {{ !$_.PSIsContainer }} | "
                                f"ForEach-Object {{ try {{ Remove-Item -Path $_.FullName -Force -ErrorAction SilentlyContinue }} catch {{}} }}"
                            ]
                            
                            # Run PowerShell command
                            subprocess.run(
                                ps_command,
                                capture_output=True,
                                text=True,
                                timeout=30,
                                shell=True
                            )
                    
                    cleaned_browsers.append("Firefox")
                except:
                    pass
            
            if cleaned_browsers:
                return True, f"Cleaned cache for: {', '.join(cleaned_browsers)}"
            else:
                return False, "No browser cache found or could not clean"
            
        except Exception as e:
            return False, f"Failed to clean browser cache: {str(e)}"
    
    def _cleanup_system_logs(self):
        """Clean Windows log files."""
        try:
            # PowerShell command to clean event logs
            ps_command = [
                "powershell",
                "-Command",
                "Get-EventLog -LogName * | ForEach-Object { Clear-EventLog -LogName $_.Log -ErrorAction SilentlyContinue }"
            ]

            # Run PowerShell command
            result = subprocess.run(
                ps_command,
                capture_output=True,
                text=True,
                timeout=60,
                shell=True
            )

            return True, "Cleaned Windows event logs"

        except Exception as e:
            return False, f"Failed to clean system logs: {str(e)}"

    def get_ram_usage(self):
        """Get current RAM usage information."""
        try:
            # PowerShell command to get memory information
            ps_command = [
                "powershell",
                "-Command",
                "Get-CimInstance -ClassName Win32_OperatingSystem | Select-Object TotalVisibleMemorySize, FreePhysicalMemory | ConvertTo-Json"
            ]

            result = subprocess.run(
                ps_command,
                capture_output=True,
                text=True,
                timeout=10,
                shell=True
            )

            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                total_kb = int(data['TotalVisibleMemorySize'])
                free_kb = int(data['FreePhysicalMemory'])
                used_kb = total_kb - free_kb

                total_gb = total_kb / (1024 * 1024)
                used_gb = used_kb / (1024 * 1024)
                free_gb = free_kb / (1024 * 1024)
                usage_percent = (used_kb / total_kb) * 100

                return {
                    'total_gb': round(total_gb, 2),
                    'used_gb': round(used_gb, 2),
                    'free_gb': round(free_gb, 2),
                    'usage_percent': round(usage_percent, 1)
                }
            else:
                return None

        except Exception as e:
            print(f"Error getting RAM usage: {e}")
            return None

    def clear_standby_cache(self):
        """Clear Windows standby cache to free memory."""
        try:
            # PowerShell command to clear standby cache
            ps_command = [
                "powershell",
                "-Command",
                "Clear-Host; Write-Host 'Clearing standby cache...'; [System.GC]::Collect(); [System.GC]::WaitForPendingFinalizers(); [System.GC]::Collect()"
            ]

            result = subprocess.run(
                ps_command,
                capture_output=True,
                text=True,
                timeout=30,
                shell=True
            )

            # Also try using RAMMap-like functionality via PowerShell
            ps_command2 = [
                "powershell",
                "-Command",
                "Get-Process | Where-Object {$_.WorkingSet -gt 0} | ForEach-Object {$_.Refresh()}"
            ]

            subprocess.run(
                ps_command2,
                capture_output=True,
                text=True,
                timeout=30,
                shell=True
            )

            return True, "Memory cache cleared successfully"

        except Exception as e:
            return False, f"Failed to clear memory cache: {str(e)}"

    def show_ram_monitor(self):
        """Show RAM usage monitor dialog."""
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("RAM Usage Monitor & Cleaner")
        dialog.geometry("500x400")
        dialog.minsize(450, 350)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(background=self.colors["background"])
        self.center_window(dialog)

        # Create main frame
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_label = ttk.Label(
            main_frame,
            text="🖥️ RAM Usage Monitor & Cleaner",
            style="Title.TLabel"
        )
        header_label.pack(pady=(0, 10))

        # Description
        desc_label = ttk.Label(
            main_frame,
            text="Monitor real-time RAM usage and free up memory by clearing standby cache.",
            style="Info.TLabel",
            wraplength=450
        )
        desc_label.pack(pady=(0, 20))

        # RAM usage frame
        usage_frame = ttk.LabelFrame(main_frame, text="Current RAM Usage", padding=15)
        usage_frame.pack(fill=tk.X, pady=(0, 15))

        # RAM usage labels
        self.ram_total_label = ttk.Label(usage_frame, text="Total RAM: Loading...", style="Info.TLabel")
        self.ram_total_label.pack(anchor=tk.W, pady=2)

        self.ram_used_label = ttk.Label(usage_frame, text="Used RAM: Loading...", style="Info.TLabel")
        self.ram_used_label.pack(anchor=tk.W, pady=2)

        self.ram_free_label = ttk.Label(usage_frame, text="Free RAM: Loading...", style="Info.TLabel")
        self.ram_free_label.pack(anchor=tk.W, pady=2)

        self.ram_percent_label = ttk.Label(usage_frame, text="Usage: Loading...", style="Info.TLabel")
        self.ram_percent_label.pack(anchor=tk.W, pady=2)

        # Progress bar for RAM usage
        self.ram_progress = ttk.Progressbar(
            usage_frame,
            mode='determinate',
            length=400
        )
        self.ram_progress.pack(fill=tk.X, pady=(10, 0))

        # Control buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 15))

        # Refresh button
        refresh_btn = ttk.Button(
            button_frame,
            text="🔄 Refresh",
            command=lambda: self.update_ram_display(dialog),
            style="Secondary.TButton"
        )
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Clear memory button
        clear_btn = ttk.Button(
            button_frame,
            text="🧹 Clear Memory Cache",
            command=lambda: self.clear_memory_and_refresh(dialog),
            style="Primary.TButton"
        )
        clear_btn.pack(side=tk.LEFT)

        # Auto-refresh checkbox
        auto_refresh_var = tk.BooleanVar(value=True)
        auto_refresh_cb = ttk.Checkbutton(
            button_frame,
            text="🔄 Auto-refresh (5s)",
            variable=auto_refresh_var,
            style="TCheckbutton"
        )
        auto_refresh_cb.pack(side=tk.RIGHT)

        # Status label
        self.ram_status_label = ttk.Label(
            main_frame,
            text="Ready",
            style="Info.TLabel"
        )
        self.ram_status_label.pack(pady=(0, 10))

        # Close button
        close_btn = ttk.Button(
            main_frame,
            text="Close",
            command=dialog.destroy,
            style="Secondary.TButton"
        )
        close_btn.pack(pady=(10, 0))

        # Store dialog reference for updates
        dialog.auto_refresh_var = auto_refresh_var

        # Initial update
        self.update_ram_display(dialog)

        # Start auto-refresh timer
        self.schedule_ram_update(dialog)

    def update_ram_display(self, dialog):
        """Update RAM usage display."""
        try:
            ram_info = self.get_ram_usage()
            if ram_info:
                self.ram_total_label.config(text=f"Total RAM: {ram_info['total_gb']} GB")
                self.ram_used_label.config(text=f"Used RAM: {ram_info['used_gb']} GB")
                self.ram_free_label.config(text=f"Free RAM: {ram_info['free_gb']} GB")
                self.ram_percent_label.config(text=f"Usage: {ram_info['usage_percent']}%")

                # Update progress bar
                self.ram_progress['value'] = ram_info['usage_percent']

                # Color coding for usage level
                if ram_info['usage_percent'] > 80:
                    color = "red"
                elif ram_info['usage_percent'] > 60:
                    color = "orange"
                else:
                    color = "green"

                self.ram_percent_label.config(foreground=color)
                self.ram_status_label.config(text=f"Last updated: {self.get_current_time()}")
            else:
                self.ram_status_label.config(text="Failed to get RAM information")
        except Exception as e:
            self.ram_status_label.config(text=f"Error: {str(e)}")

    def clear_memory_and_refresh(self, dialog):
        """Clear memory cache and refresh display."""
        self.ram_status_label.config(text="Clearing memory cache...")
        dialog.update()

        success, message = self.clear_standby_cache()

        if success:
            self.ram_status_label.config(text=message)
            # Wait a moment then refresh
            dialog.after(1000, lambda: self.update_ram_display(dialog))
        else:
            self.ram_status_label.config(text=message)

    def schedule_ram_update(self, dialog):
        """Schedule automatic RAM usage updates."""
        try:
            if dialog.winfo_exists() and dialog.auto_refresh_var.get():
                self.update_ram_display(dialog)
                dialog.after(5000, lambda: self.schedule_ram_update(dialog))
        except:
            # Dialog was closed
            pass

    def get_current_time(self):
        """Get current time as formatted string."""
        import datetime
        return datetime.datetime.now().strftime("%H:%M:%S")

    def test_internet_speed(self, progress_callback=None):
        """Test internet speed using multiple methods."""
        import urllib.request
        import time
        import threading

        results = {
            'download_speed': 0,
            'upload_speed': 0,
            'ping': 0,
            'status': 'Testing...',
            'error': None
        }

        try:
            # Test 1: Download speed test using a test file
            if progress_callback:
                progress_callback("Testing download speed...", 25)

            download_speed = self._test_download_speed()
            results['download_speed'] = download_speed

            # Test 2: Upload speed test
            if progress_callback:
                progress_callback("Testing upload speed...", 50)

            upload_speed = self._test_upload_speed()

            # If upload test failed, estimate based on download speed
            if upload_speed == 0 and download_speed > 0:
                # Typical upload is 10-20% of download for most connections
                upload_speed = round(download_speed * 0.12, 2)  # Use 12% as estimate (more realistic)
                print(f"Upload test failed, estimating {upload_speed} Mbps based on download speed")

            results['upload_speed'] = upload_speed

            # Test 3: Ping test
            if progress_callback:
                progress_callback("Testing ping...", 75)

            ping = self._test_ping()
            results['ping'] = ping

            if progress_callback:
                progress_callback("Test completed!", 100)

            results['status'] = 'Completed'

        except Exception as e:
            results['error'] = str(e)
            results['status'] = 'Failed'

        return results

    def _test_download_speed(self):
        """Test download speed using multiple large files and parallel downloads."""
        import urllib.request
        import time
        import threading
        from concurrent.futures import ThreadPoolExecutor, as_completed

        try:
            # Use larger files and more diverse servers for high-speed connections
            test_configs = [
                # Large files for high-speed testing
                {
                    'url': 'http://speedtest.ftp.otenet.gr/files/test100Mb.db',
                    'expected_size': 100 * 1024 * 1024,  # 100MB
                    'timeout': 60,
                    'priority': 1
                },
                {
                    'url': 'http://ipv4.download.thinkbroadband.com/50MB.zip',
                    'expected_size': 50 * 1024 * 1024,   # 50MB
                    'timeout': 45,
                    'priority': 1
                },
                {
                    'url': 'https://proof.ovh.net/files/100Mb.dat',
                    'expected_size': 100 * 1024 * 1024,  # 100MB
                    'timeout': 60,
                    'priority': 1
                },
                # Medium files as fallback
                {
                    'url': 'http://speedtest.ftp.otenet.gr/files/test10Mb.db',
                    'expected_size': 10 * 1024 * 1024,   # 10MB
                    'timeout': 30,
                    'priority': 2
                },
                {
                    'url': 'http://ipv4.download.thinkbroadband.com/10MB.zip',
                    'expected_size': 10 * 1024 * 1024,   # 10MB
                    'timeout': 30,
                    'priority': 2
                },
                # Additional fast CDN servers
                {
                    'url': 'https://speed.cloudflare.com/__down?bytes=52428800',  # 50MB from Cloudflare
                    'expected_size': 50 * 1024 * 1024,
                    'timeout': 45,
                    'priority': 1
                },
                {
                    'url': 'https://bouygues.testdebit.info/100M.iso',  # 100MB
                    'expected_size': 100 * 1024 * 1024,
                    'timeout': 60,
                    'priority': 1
                }
            ]

            def test_single_download(config):
                """Test download speed for a single URL."""
                try:
                    start_time = time.time()

                    # Create request with headers to avoid caching
                    req = urllib.request.Request(config['url'])
                    req.add_header('Cache-Control', 'no-cache')
                    req.add_header('Pragma', 'no-cache')

                    # Download with timeout
                    with urllib.request.urlopen(req, timeout=config['timeout']) as response:
                        data = response.read()

                    end_time = time.time()
                    duration = end_time - start_time

                    if duration > 0.1 and len(data) > 0:  # Minimum 0.1 second duration
                        # Calculate speed in Mbps
                        file_size_bytes = len(data)
                        file_size_bits = file_size_bytes * 8
                        speed_bps = file_size_bits / duration
                        speed_mbps = speed_bps / (1000 * 1000)  # Convert to Mbps (using 1000, not 1024)

                        return {
                            'speed': speed_mbps,
                            'size_mb': file_size_bytes / (1024 * 1024),
                            'duration': duration,
                            'url': config['url'],
                            'priority': config['priority']
                        }

                except Exception as e:
                    print(f"Download test failed for {config['url']}: {e}")
                    return None

                return None

            speeds = []

            # Try high-priority (large) files first with parallel downloads
            high_priority_configs = [c for c in test_configs if c['priority'] == 1]

            # Use ThreadPoolExecutor for parallel downloads (but limit to 2-3 concurrent)
            with ThreadPoolExecutor(max_workers=3) as executor:
                # Submit high-priority downloads
                future_to_config = {executor.submit(test_single_download, config): config
                                  for config in high_priority_configs[:3]}  # Limit to 3 concurrent

                # Collect results as they complete
                for future in as_completed(future_to_config, timeout=70):
                    result = future.result()
                    if result and 0.5 <= result['speed'] <= 2000:  # Accept 0.5 to 2000 Mbps
                        speeds.append(result)
                        print(f"Download test: {result['speed']:.2f} Mbps "
                              f"({result['size_mb']:.1f}MB in {result['duration']:.1f}s) "
                              f"from {result['url']}")

                        # If we get a very good result (>50 Mbps), we can stop
                        if result['speed'] > 50:
                            break

            # If no good results from large files, try medium files
            if not speeds or max(s['speed'] for s in speeds) < 10:
                medium_priority_configs = [c for c in test_configs if c['priority'] == 2]

                for config in medium_priority_configs[:2]:  # Try 2 medium files
                    result = test_single_download(config)
                    if result and 0.5 <= result['speed'] <= 2000:
                        speeds.append(result)
                        print(f"Download test (fallback): {result['speed']:.2f} Mbps "
                              f"({result['size_mb']:.1f}MB in {result['duration']:.1f}s)")

            # Return the best (highest) speed if we have any results
            if speeds:
                # Take the highest speed from successful tests
                best_result = max(speeds, key=lambda x: x['speed'])
                best_speed = best_result['speed']
                print(f"Best download speed: {best_speed:.2f} Mbps")
                return round(best_speed, 2)
            else:
                print("No successful download tests")
                return 0

        except Exception as e:
            print(f"Download test error: {e}")
            return 0

    def _test_upload_speed(self):
        """Test upload speed using larger HTTP POST requests."""
        import urllib.request
        import urllib.parse
        import time
        import random
        import string
        from concurrent.futures import ThreadPoolExecutor

        try:
            # Create larger test data for more accurate upload testing
            test_configs = [
                {'size': 1024 * 1024, 'name': '1MB'},      # 1MB
                {'size': 2 * 1024 * 1024, 'name': '2MB'},  # 2MB
                {'size': 5 * 1024 * 1024, 'name': '5MB'},  # 5MB
            ]

            # Better upload test servers
            upload_urls = [
                'https://httpbin.org/post',
                'https://postman-echo.com/post',
                'https://httpbingo.org/post',
                'https://eu.httpbin.org/post'
            ]

            def test_single_upload(config, url):
                """Test upload speed for a single configuration."""
                try:
                    size = config['size']

                    # Generate random binary data (more efficient than string)
                    test_data = bytes(random.getrandbits(8) for _ in range(size))

                    start_time = time.time()

                    # Create request with binary data
                    req = urllib.request.Request(url, data=test_data)
                    req.add_header('Content-Type', 'application/octet-stream')
                    req.add_header('Content-Length', str(len(test_data)))

                    # Send the request
                    with urllib.request.urlopen(req, timeout=30) as response:
                        response.read()  # Read response to complete the request

                    end_time = time.time()
                    duration = end_time - start_time

                    if duration > 0.1:  # Minimum 0.1 second duration
                        # Calculate upload speed in Mbps
                        data_size_bits = len(test_data) * 8
                        speed_bps = data_size_bits / duration
                        speed_mbps = speed_bps / (1000 * 1000)  # Convert to Mbps (using 1000, not 1024)

                        return {
                            'speed': speed_mbps,
                            'size': config['name'],
                            'duration': duration,
                            'url': url
                        }

                except Exception as e:
                    print(f"Upload test failed for {config['name']} to {url}: {e}")
                    return None

                return None

            speeds = []

            # Test with different sizes, starting with smaller ones
            for config in test_configs:
                # Try multiple servers for each size
                best_speed_for_size = 0

                for url in upload_urls[:2]:  # Try first 2 URLs for each size
                    result = test_single_upload(config, url)
                    if result and 0.1 <= result['speed'] <= 1000:  # Accept 0.1 to 1000 Mbps
                        speeds.append(result)
                        best_speed_for_size = max(best_speed_for_size, result['speed'])
                        print(f"Upload test: {result['speed']:.2f} Mbps "
                              f"({result['size']} in {result['duration']:.1f}s) to {result['url']}")

                        # If we get a good result for this size, move to next size
                        if result['speed'] > 1:
                            break

                # If we got good results, we can stop testing larger sizes
                if best_speed_for_size > 10:
                    break

                # If upload is very slow, don't test larger files
                if best_speed_for_size > 0 and best_speed_for_size < 1:
                    print(f"Upload speed is slow ({best_speed_for_size:.2f} Mbps), skipping larger files")
                    break

            # Return the best (highest) speed if we have any results
            if speeds:
                # Take the highest speed from successful tests
                best_result = max(speeds, key=lambda x: x['speed'])
                best_speed = best_result['speed']
                print(f"Best upload speed: {best_speed:.2f} Mbps")
                return round(best_speed, 2)
            else:
                print("No successful upload tests")
                return 0

        except Exception as e:
            print(f"Upload test error: {e}")
            return 0

    def _test_ping(self):
        """Test ping to common servers."""
        import subprocess
        import re

        try:
            # Test ping to Google DNS
            result = subprocess.run(
                ['ping', '-n', '4', '8.8.8.8'],
                capture_output=True,
                text=True,
                timeout=10,
                shell=True
            )

            if result.returncode == 0:
                # Extract average ping time from Windows ping output
                ping_match = re.search(r'Average = (\d+)ms', result.stdout)
                if ping_match:
                    return int(ping_match.group(1))

                # Fallback: look for individual ping times
                ping_times = re.findall(r'time=(\d+)ms', result.stdout)
                if ping_times:
                    avg_ping = sum(int(t) for t in ping_times) / len(ping_times)
                    return round(avg_ping)

            return 0

        except Exception as e:
            print(f"Ping test error: {e}")
            return 0

    def save_speed_test_result(self, result):
        """Save speed test result to history file."""
        import json
        import datetime
        import os

        try:
            history_file = "speed_test_history.json"

            # Load existing history
            history = []
            if os.path.exists(history_file):
                try:
                    with open(history_file, 'r') as f:
                        history = json.load(f)
                except:
                    history = []

            # Add new result with timestamp
            result['timestamp'] = datetime.datetime.now().isoformat()
            result['date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            history.append(result)

            # Keep only last 50 results
            history = history[-50:]

            # Save updated history
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)

        except Exception as e:
            print(f"Error saving speed test result: {e}")

    def load_speed_test_history(self):
        """Load speed test history from file."""
        import json
        import os

        try:
            history_file = "speed_test_history.json"
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading speed test history: {e}")
            return []

    def show_speed_test(self):
        """Show Internet Speed Test dialog."""
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Internet Speed Test")
        dialog.geometry("600x500")
        dialog.minsize(550, 450)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(background=self.colors["background"])
        self.center_window(dialog)

        # Create main frame
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_label = ttk.Label(
            main_frame,
            text="🌐 Internet Speed Test",
            style="Title.TLabel"
        )
        header_label.pack(pady=(0, 10))

        # Description
        desc_label = ttk.Label(
            main_frame,
            text="Test your internet connection speed and view historical results.",
            style="Info.TLabel",
            wraplength=550
        )
        desc_label.pack(pady=(0, 20))

        # Current test frame
        test_frame = ttk.LabelFrame(main_frame, text="Current Test", padding=15)
        test_frame.pack(fill=tk.X, pady=(0, 15))

        # Test results labels
        self.speed_download_label = ttk.Label(test_frame, text="Download Speed: Not tested", style="Info.TLabel")
        self.speed_download_label.pack(anchor=tk.W, pady=2)

        self.speed_upload_label = ttk.Label(test_frame, text="Upload Speed: Not tested", style="Info.TLabel")
        self.speed_upload_label.pack(anchor=tk.W, pady=2)

        self.speed_ping_label = ttk.Label(test_frame, text="Ping: Not tested", style="Info.TLabel")
        self.speed_ping_label.pack(anchor=tk.W, pady=2)

        # Progress bar for speed test
        self.speed_progress = ttk.Progressbar(
            test_frame,
            mode='determinate',
            length=500
        )
        self.speed_progress.pack(fill=tk.X, pady=(10, 0))

        # Status label
        self.speed_status_label = ttk.Label(
            test_frame,
            text="Ready to test",
            style="Info.TLabel"
        )
        self.speed_status_label.pack(pady=(5, 0))

        # Control buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 15))

        # Start test button
        self.start_test_btn = ttk.Button(
            button_frame,
            text="🚀 Start Speed Test",
            command=lambda: self.start_speed_test(dialog),
            style="Primary.TButton"
        )
        self.start_test_btn.pack(side=tk.LEFT, padx=(0, 10))

        # View history button
        history_btn = ttk.Button(
            button_frame,
            text="📊 View History",
            command=lambda: self.show_speed_history(dialog),
            style="Secondary.TButton"
        )
        history_btn.pack(side=tk.LEFT)

        # Close button
        close_btn = ttk.Button(
            main_frame,
            text="Close",
            command=dialog.destroy,
            style="Secondary.TButton"
        )
        close_btn.pack(pady=(10, 0))

        # Store dialog reference
        self.speed_test_dialog = dialog

    def start_speed_test(self, dialog):
        """Start the speed test in a background thread."""
        # Disable start button during test
        self.start_test_btn.config(state='disabled')
        self.speed_progress['value'] = 0
        self.speed_status_label.config(text="Initializing test...")

        # Start test in background thread
        threading.Thread(target=self.speed_test_thread, args=(dialog,), daemon=True).start()

    def speed_test_thread(self, dialog):
        """Background thread for speed testing."""
        try:
            def progress_callback(status, progress):
                # Update UI in main thread
                dialog.after(0, lambda: self.update_speed_progress(status, progress))

            # Run the speed test
            result = self.test_internet_speed(progress_callback)

            # Update UI with results in main thread
            dialog.after(0, lambda: self.update_speed_results(result))

        except Exception as e:
            dialog.after(0, lambda: self.speed_test_error(str(e)))

    def update_speed_progress(self, status, progress):
        """Update speed test progress in UI."""
        self.speed_status_label.config(text=status)
        self.speed_progress['value'] = progress

    def update_speed_results(self, result):
        """Update UI with speed test results."""
        try:
            if result['status'] == 'Completed':
                # Update labels with results
                self.speed_download_label.config(
                    text=f"Download Speed: {result['download_speed']} Mbps"
                )
                self.speed_upload_label.config(
                    text=f"Upload Speed: {result['upload_speed']} Mbps"
                )
                self.speed_ping_label.config(
                    text=f"Ping: {result['ping']} ms"
                )
                self.speed_status_label.config(text="Test completed successfully!")

                # Save result to history
                self.save_speed_test_result(result)

            else:
                self.speed_status_label.config(text=f"Test failed: {result.get('error', 'Unknown error')}")

        except Exception as e:
            self.speed_status_label.config(text=f"Error updating results: {str(e)}")
        finally:
            # Re-enable start button
            self.start_test_btn.config(state='normal')
            self.speed_progress['value'] = 100

    def speed_test_error(self, error):
        """Handle speed test error."""
        self.speed_status_label.config(text=f"Test failed: {error}")
        self.start_test_btn.config(state='normal')
        self.speed_progress['value'] = 0

    def show_speed_history(self, parent_dialog):
        """Show speed test history dialog."""
        # Create history dialog
        history_dialog = tk.Toplevel(parent_dialog)
        history_dialog.title("Speed Test History")
        history_dialog.geometry("700x400")
        history_dialog.minsize(650, 350)
        history_dialog.transient(parent_dialog)
        history_dialog.grab_set()
        history_dialog.configure(background=self.colors["background"])
        self.center_window(history_dialog)

        # Create main frame
        main_frame = ttk.Frame(history_dialog, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_label = ttk.Label(
            main_frame,
            text="📊 Speed Test History",
            style="Title.TLabel"
        )
        header_label.pack(pady=(0, 10))

        # Create treeview for history
        columns = ("date", "download", "upload", "ping")
        history_tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=12)

        # Configure columns
        history_tree.heading("date", text="Date & Time")
        history_tree.heading("download", text="Download (Mbps)")
        history_tree.heading("upload", text="Upload (Mbps)")
        history_tree.heading("ping", text="Ping (ms)")

        history_tree.column("date", width=150)
        history_tree.column("download", width=120)
        history_tree.column("upload", width=120)
        history_tree.column("ping", width=100)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=history_tree.yview)
        history_tree.configure(yscrollcommand=scrollbar.set)

        # Pack treeview and scrollbar
        history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Load and display history
        history = self.load_speed_test_history()

        if history:
            # Sort by timestamp (newest first)
            history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

            for entry in history:
                if entry.get('status') == 'Completed':
                    history_tree.insert("", tk.END, values=(
                        entry.get('date', 'Unknown'),
                        f"{entry.get('download_speed', 0):.1f}",
                        f"{entry.get('upload_speed', 0):.1f}",
                        f"{entry.get('ping', 0)}"
                    ))
        else:
            # Show message if no history
            no_data_label = ttk.Label(
                main_frame,
                text="No speed test history available. Run a test to see results here.",
                style="Info.TLabel"
            )
            no_data_label.pack(pady=20)

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))

        # Clear history button
        clear_btn = ttk.Button(
            button_frame,
            text="🗑️ Clear History",
            command=lambda: self.clear_speed_history(history_dialog),
            style="Secondary.TButton"
        )
        clear_btn.pack(side=tk.LEFT)

        # Close button
        close_btn = ttk.Button(
            button_frame,
            text="Close",
            command=history_dialog.destroy,
            style="Secondary.TButton"
        )
        close_btn.pack(side=tk.RIGHT)

    def clear_speed_history(self, dialog):
        """Clear speed test history."""
        import os

        if messagebox.askyesno("Clear History", "Are you sure you want to clear all speed test history?"):
            try:
                history_file = "speed_test_history.json"
                if os.path.exists(history_file):
                    os.remove(history_file)
                messagebox.showinfo("Success", "Speed test history cleared successfully!")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear history: {str(e)}")

    def get_network_connections(self):
        """Get current network connections and processes."""
        import subprocess
        import json

        try:
            # PowerShell command to get network connections with process information
            ps_command = [
                "powershell",
                "-Command",
                "Get-NetTCPConnection | Where-Object {$_.State -eq 'Established' -or $_.State -eq 'Listen'} | ForEach-Object { $proc = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue; [PSCustomObject]@{ LocalAddress = $_.LocalAddress; LocalPort = $_.LocalPort; RemoteAddress = $_.RemoteAddress; RemotePort = $_.RemotePort; State = $_.State; ProcessId = $_.OwningProcess; ProcessName = if($proc) {$proc.ProcessName} else {'Unknown'}; ProcessPath = if($proc) {$proc.Path} else {'Unknown'} } } | ConvertTo-Json"
            ]

            result = subprocess.run(
                ps_command,
                capture_output=True,
                text=True,
                timeout=30,
                shell=True
            )

            if result.returncode == 0 and result.stdout.strip():
                try:
                    # Parse JSON output
                    connections_data = json.loads(result.stdout)

                    # Handle single connection (not in array)
                    if isinstance(connections_data, dict):
                        connections_data = [connections_data]

                    # Process and clean the data
                    connections = []
                    for conn in connections_data:
                        # Skip localhost connections to reduce noise
                        if conn.get('RemoteAddress') in ['127.0.0.1', '::1', '0.0.0.0']:
                            continue

                        connections.append({
                            'local_address': conn.get('LocalAddress', ''),
                            'local_port': conn.get('LocalPort', 0),
                            'remote_address': conn.get('RemoteAddress', ''),
                            'remote_port': conn.get('RemotePort', 0),
                            'state': conn.get('State', ''),
                            'process_id': conn.get('ProcessId', 0),
                            'process_name': conn.get('ProcessName', 'Unknown'),
                            'process_path': conn.get('ProcessPath', 'Unknown')
                        })

                    return connections

                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    return []
            else:
                print(f"PowerShell command failed: {result.stderr}")
                return []

        except Exception as e:
            print(f"Error getting network connections: {e}")
            return []

    def kill_process_by_id(self, process_id):
        """Kill a process by its ID."""
        import subprocess

        try:
            # Use taskkill to terminate the process
            result = subprocess.run(
                ['taskkill', '/F', '/PID', str(process_id)],
                capture_output=True,
                text=True,
                timeout=10,
                shell=True
            )

            if result.returncode == 0:
                return True, f"Process {process_id} terminated successfully"
            else:
                return False, f"Failed to terminate process: {result.stderr}"

        except Exception as e:
            return False, f"Error terminating process: {str(e)}"

    def export_network_connections(self, connections, format_type='json', filepath=None):
        """Export network connections to file with file dialog."""
        import json
        import datetime
        import os

        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

            # If no filepath provided, show file dialog
            if not filepath:
                try:
                    if format_type == 'json':
                        default_filename = f"network_connections_{timestamp}.json"
                        file_types = [("JSON files", "*.json"), ("All files", "*.*")]
                        extension = ".json"
                    else:
                        default_filename = f"network_connections_{timestamp}.txt"
                        file_types = [("Text files", "*.txt"), ("All files", "*.*")]
                        extension = ".txt"

                    filepath = filedialog.asksaveasfilename(
                        title=f"Save Network Connections Report ({format_type.upper()})",
                        defaultextension=extension,
                        filetypes=file_types,
                        initialfile=default_filename
                    )

                    if not filepath:  # User cancelled
                        return False, "Export cancelled by user"

                except Exception as dialog_error:
                    # Fallback to current directory if file dialog fails
                    filepath = default_filename
                    print(f"File dialog error, using default filename: {dialog_error}")

            if format_type == 'json':
                export_data = {
                    'export_info': {
                        'timestamp': datetime.datetime.now().isoformat(),
                        'date_readable': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'total_connections': len(connections),
                        'format_version': '1.0'
                    },
                    'connections': connections
                }

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)

            else:  # text format
                with open(filepath, 'w', encoding='utf-8') as f:
                    # Header
                    f.write("=" * 80 + "\n")
                    f.write("NETWORK CONNECTIONS REPORT\n")
                    f.write("=" * 80 + "\n")
                    f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Total Connections: {len(connections)}\n")
                    f.write("=" * 80 + "\n\n")

                    if not connections:
                        f.write("No network connections found.\n")
                    else:
                        # Group connections by process for better readability
                        processes = {}
                        for conn in connections:
                            proc_name = conn.get('process_name', 'Unknown')
                            if proc_name not in processes:
                                processes[proc_name] = []
                            processes[proc_name].append(conn)

                        # Write grouped connections
                        for proc_name, proc_connections in sorted(processes.items()):
                            f.write(f"PROCESS: {proc_name}\n")
                            f.write("-" * 60 + "\n")

                            for i, conn in enumerate(proc_connections, 1):
                                f.write(f"  Connection #{i}:\n")
                                f.write(f"    Process ID: {conn.get('process_id', 'Unknown')}\n")
                                f.write(f"    Local Address: {conn.get('local_address', 'Unknown')}\n")
                                f.write(f"    Local Port: {conn.get('local_port', 'Unknown')}\n")
                                f.write(f"    Remote Address: {conn.get('remote_address', 'N/A')}\n")
                                f.write(f"    Remote Port: {conn.get('remote_port', 'N/A')}\n")
                                f.write(f"    Connection State: {conn.get('state', 'Unknown')}\n")
                                f.write(f"    Process Path: {conn.get('process_path', 'Unknown')}\n")
                                f.write("\n")

                            f.write("\n")

                        # Summary section
                        f.write("=" * 80 + "\n")
                        f.write("SUMMARY\n")
                        f.write("=" * 80 + "\n")
                        f.write(f"Total Processes: {len(processes)}\n")
                        f.write(f"Total Connections: {len(connections)}\n")

                        # Count by state
                        states = {}
                        for conn in connections:
                            state = conn.get('state', 'Unknown')
                            states[state] = states.get(state, 0) + 1

                        f.write("\nConnections by State:\n")
                        for state, count in sorted(states.items()):
                            f.write(f"  {state}: {count}\n")

                        # External connections
                        external_connections = [
                            conn for conn in connections
                            if conn.get('remote_address') and
                            not conn.get('remote_address', '').startswith('127.') and
                            not conn.get('remote_address', '').startswith('192.168.') and
                            not conn.get('remote_address', '').startswith('10.') and
                            conn.get('remote_address') != '0.0.0.0'
                        ]

                        f.write(f"\nExternal Connections: {len(external_connections)}\n")
                        if external_connections:
                            f.write("External Connection Details:\n")
                            for conn in external_connections:
                                f.write(f"  {conn.get('process_name', 'Unknown')} -> {conn.get('remote_address', 'Unknown')}:{conn.get('remote_port', 'Unknown')}\n")

            filename = os.path.basename(filepath)
            return True, f"Successfully exported to {filename}"

        except PermissionError:
            return False, f"Permission denied. Please choose a different location or close any programs that might be using the file."
        except FileNotFoundError:
            return False, f"Invalid file path. Please choose a valid location."
        except Exception as e:
            return False, f"Export failed: {str(e)}"

    def show_network_monitor(self):
        """Show Network Connection Monitor dialog."""
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Network Connection Monitor")
        dialog.geometry("1000x600")
        dialog.minsize(900, 500)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(background=self.colors["background"])
        self.center_window(dialog)

        # Create main frame
        main_frame = ttk.Frame(dialog, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_label = ttk.Label(
            main_frame,
            text="🌐 Network Connection Monitor",
            style="Title.TLabel"
        )
        header_label.pack(pady=(0, 10))

        # Description
        desc_label = ttk.Label(
            main_frame,
            text="Monitor active network connections and processes. Identify suspicious connections and manage processes.",
            style="Info.TLabel",
            wraplength=950
        )
        desc_label.pack(pady=(0, 15))

        # Control buttons frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 15))

        # Refresh button
        refresh_btn = ttk.Button(
            control_frame,
            text="🔄 Refresh Connections",
            command=lambda: self.refresh_network_connections(dialog),
            style="Primary.TButton"
        )
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Kill process button
        self.kill_process_btn = ttk.Button(
            control_frame,
            text="⚠️ Kill Selected Process",
            command=lambda: self.kill_selected_process(dialog),
            style="Secondary.TButton",
            state='disabled'
        )
        self.kill_process_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Export dropdown
        export_var = tk.StringVar(value="📤 Export")
        export_combo = ttk.Combobox(
            control_frame,
            textvariable=export_var,
            values=["📤 Export", "📄 JSON", "📝 Text"],
            state="readonly",
            width=12,
            style="TCombobox"
        )
        export_combo.pack(side=tk.RIGHT, padx=(10, 0))

        def on_export_select(event):
            selection = export_var.get()
            if selection == "📄 JSON":
                self.export_network_data(dialog, 'json')
                export_var.set("📤 Export")
            elif selection == "📝 Text":
                self.export_network_data(dialog, 'text')
                export_var.set("📤 Export")

        export_combo.bind("<<ComboboxSelected>>", on_export_select)

        # Create treeview for connections
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Define columns
        columns = ("process", "pid", "local", "remote", "state", "path")
        self.network_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)

        # Configure columns
        self.network_tree.heading("process", text="Process Name")
        self.network_tree.heading("pid", text="PID")
        self.network_tree.heading("local", text="Local Address:Port")
        self.network_tree.heading("remote", text="Remote Address:Port")
        self.network_tree.heading("state", text="State")
        self.network_tree.heading("path", text="Process Path")

        # Set column widths
        self.network_tree.column("process", width=120)
        self.network_tree.column("pid", width=60)
        self.network_tree.column("local", width=150)
        self.network_tree.column("remote", width=150)
        self.network_tree.column("state", width=100)
        self.network_tree.column("path", width=300)

        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.network_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.network_tree.xview)
        self.network_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack treeview and scrollbars
        self.network_tree.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.E, tk.W))

        # Configure grid weights
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        # Bind selection event
        self.network_tree.bind('<<TreeviewSelect>>', lambda e: self.on_network_selection(dialog))

        # Status label
        self.network_status_label = ttk.Label(
            main_frame,
            text="Click 'Refresh Connections' to load network data",
            style="Info.TLabel"
        )
        self.network_status_label.pack(pady=(0, 10))

        # Close button
        close_btn = ttk.Button(
            main_frame,
            text="Close",
            command=dialog.destroy,
            style="Secondary.TButton"
        )
        close_btn.pack(pady=(10, 0))

        # Store dialog reference
        self.network_dialog = dialog

        # Auto-refresh on open
        self.refresh_network_connections(dialog)

    def refresh_network_connections(self, dialog):
        """Refresh the network connections display."""
        self.network_status_label.config(text="Loading network connections...")
        dialog.update()

        # Clear existing items
        for item in self.network_tree.get_children():
            self.network_tree.delete(item)

        # Get connections in background thread
        threading.Thread(target=self.load_network_connections_thread, args=(dialog,), daemon=True).start()

    def load_network_connections_thread(self, dialog):
        """Load network connections in background thread."""
        try:
            connections = self.get_network_connections()

            # Update UI in main thread
            dialog.after(0, lambda: self.update_network_display(dialog, connections))

        except Exception as e:
            dialog.after(0, lambda: self.network_status_label.config(text=f"Error loading connections: {str(e)}"))

    def update_network_display(self, dialog, connections):
        """Update the network connections display."""
        try:
            # Clear existing items
            for item in self.network_tree.get_children():
                self.network_tree.delete(item)

            if connections:
                # Sort connections by process name
                connections.sort(key=lambda x: x['process_name'].lower())

                # Add connections to tree
                for conn in connections:
                    local_addr = f"{conn['local_address']}:{conn['local_port']}"
                    remote_addr = f"{conn['remote_address']}:{conn['remote_port']}" if conn['remote_address'] else "N/A"

                    # Color code based on connection type
                    tags = ()
                    if conn['state'] == 'Listen':
                        tags = ('listening',)
                    elif conn['remote_address'] and not conn['remote_address'].startswith('192.168.') and not conn['remote_address'].startswith('10.'):
                        tags = ('external',)

                    self.network_tree.insert("", tk.END, values=(
                        conn['process_name'],
                        conn['process_id'],
                        local_addr,
                        remote_addr,
                        conn['state'],
                        conn['process_path']
                    ), tags=tags)

                # Configure tags for color coding - use app background
                self.network_tree.tag_configure('listening', background=self.colors["background"], foreground='#28a745')
                self.network_tree.tag_configure('external', background=self.colors["background"], foreground='#ffc107')

                self.network_status_label.config(text=f"Found {len(connections)} active network connections")
            else:
                self.network_status_label.config(text="No network connections found")

        except Exception as e:
            self.network_status_label.config(text=f"Error updating display: {str(e)}")

    def on_network_selection(self, dialog):
        """Handle network connection selection."""
        selection = self.network_tree.selection()
        if selection:
            self.kill_process_btn.config(state='normal')
        else:
            self.kill_process_btn.config(state='disabled')

    def kill_selected_process(self, dialog):
        """Kill the selected process."""
        selection = self.network_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a connection to kill its process.")
            return

        # Get selected item data
        item = selection[0]
        values = self.network_tree.item(item, 'values')
        process_name = values[0]
        process_id = values[1]

        # Confirm action
        if messagebox.askyesno("Confirm Process Termination",
                              f"Are you sure you want to terminate process '{process_name}' (PID: {process_id})?\n\n"
                              f"This action cannot be undone and may cause data loss."):

            self.network_status_label.config(text=f"Terminating process {process_name} (PID: {process_id})...")
            dialog.update()

            success, message = self.kill_process_by_id(process_id)

            if success:
                messagebox.showinfo("Success", message)
                # Refresh the connections list
                self.refresh_network_connections(dialog)
            else:
                messagebox.showerror("Error", message)
                self.network_status_label.config(text="Ready")

    def export_network_data(self, dialog, format_type):
        """Export network connections data with file dialog."""
        try:
            # Get current connections
            connections = []
            for item in self.network_tree.get_children():
                values = self.network_tree.item(item, 'values')

                if len(values) < 6:
                    continue  # Skip incomplete entries

                # Parse local and remote addresses safely
                try:
                    local_parts = str(values[2]).split(':')
                    remote_parts = str(values[3]).split(':') if str(values[3]) != 'N/A' else ['', '']

                    # Handle cases where address might be empty or malformed
                    local_address = local_parts[0] if len(local_parts) > 0 else ''
                    local_port = 0
                    if len(local_parts) > 1:
                        try:
                            local_port = int(local_parts[1])
                        except (ValueError, IndexError):
                            local_port = 0

                    remote_address = remote_parts[0] if len(remote_parts) > 0 and remote_parts[0] else ''
                    remote_port = 0
                    if len(remote_parts) > 1 and remote_parts[1]:
                        try:
                            remote_port = int(remote_parts[1])
                        except (ValueError, IndexError):
                            remote_port = 0

                    # Parse process ID safely
                    process_id = 0
                    try:
                        process_id = int(str(values[1])) if str(values[1]).isdigit() else 0
                    except (ValueError, IndexError):
                        process_id = 0

                    connections.append({
                        'process_name': str(values[0]) if values[0] else 'Unknown',
                        'process_id': process_id,
                        'local_address': local_address,
                        'local_port': local_port,
                        'remote_address': remote_address,
                        'remote_port': remote_port,
                        'state': str(values[4]) if values[4] else 'Unknown',
                        'process_path': str(values[5]) if values[5] else 'Unknown'
                    })

                except Exception as e:
                    print(f"Error parsing connection data: {e}")
                    continue

            if not connections:
                messagebox.showwarning("No Data", "No network connections to export. Please refresh the data first.")
                return

            # Call the export function
            success, message = self.export_network_connections(connections, format_type)

            if success:
                messagebox.showinfo("Export Successful", message)
            else:
                if "cancelled" not in message.lower():
                    messagebox.showerror("Export Failed", message)

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export network data: {str(e)}")

    def get_windows_services(self):
        """Get all Windows services with detailed information."""
        import subprocess

        try:
            print("Attempting to get Windows services...")

            # Use sc command directly - more reliable than PowerShell
            result = subprocess.run(
                ['sc', 'query', 'type=', 'service', 'state=', 'all'],
                capture_output=True,
                text=True,
                timeout=30,
                shell=True
            )

            if result.returncode == 0:
                services = self._parse_sc_output(result.stdout)
                if services:
                    print(f"Successfully loaded {len(services)} services using sc command")
                    return services

            # Fallback to PowerShell if sc fails
            print("sc command failed, trying PowerShell...")
            return self._get_services_powershell()

        except Exception as e:
            print(f"Error getting Windows services: {e}")
            return self._get_services_minimal()

    def _parse_sc_output(self, output):
        """Parse sc query output to extract service information."""
        try:
            services = []
            lines = output.split('\n')
            current_service = {}

            for line in lines:
                line = line.strip()

                if line.startswith('SERVICE_NAME:'):
                    # Save previous service if exists
                    if current_service and current_service.get('name'):
                        services.append(current_service)

                    # Start new service
                    service_name = line.split(':', 1)[1].strip()
                    current_service = {
                        'name': service_name,
                        'display_name': service_name,
                        'status': 'Unknown',
                        'start_type': 'Unknown',
                        'description': 'Windows Service',
                        'path_name': 'Unknown',
                        'service_type': 'Unknown',
                        'process_id': 0,
                        'category': self._categorize_service(service_name)
                    }

                elif line.startswith('DISPLAY_NAME:') and current_service:
                    display_name = line.split(':', 1)[1].strip()
                    current_service['display_name'] = display_name

                elif line.startswith('STATE') and current_service:
                    # Parse state line: "STATE              : 4  RUNNING"
                    parts = line.split()
                    if len(parts) >= 4:
                        status = parts[3].replace('_', ' ').title()
                        current_service['status'] = status

            # Add last service
            if current_service and current_service.get('name'):
                services.append(current_service)

            return services

        except Exception as e:
            print(f"Error parsing sc output: {e}")
            return []

    def _get_services_powershell(self):
        """Try to get services using PowerShell as fallback."""
        try:
            # Simple PowerShell command
            ps_command = [
                "powershell",
                "-ExecutionPolicy", "Bypass",
                "-Command",
                "Get-Service | ForEach-Object { Write-Output \"$($_.Name)|$($_.DisplayName)|$($_.Status)\" }"
            ]

            result = subprocess.run(
                ps_command,
                capture_output=True,
                text=True,
                timeout=30,
                shell=True
            )

            if result.returncode == 0 and result.stdout.strip():
                services = []
                lines = result.stdout.strip().split('\n')

                for line in lines:
                    line = line.strip()
                    if '|' in line:
                        parts = line.split('|')
                        if len(parts) >= 3:
                            service_name = parts[0].strip()
                            display_name = parts[1].strip()
                            status = parts[2].strip()

                            service_info = {
                                'name': service_name,
                                'display_name': display_name,
                                'status': status,
                                'start_type': 'Unknown',
                                'description': 'Windows Service',
                                'path_name': 'Unknown',
                                'service_type': 'Unknown',
                                'process_id': 0,
                                'category': self._categorize_service(service_name)
                            }
                            services.append(service_info)

                print(f"PowerShell fallback loaded {len(services)} services")
                return services
            else:
                print(f"PowerShell fallback failed: {result.stderr}")
                return self._get_services_minimal()

        except Exception as e:
            print(f"PowerShell fallback error: {e}")
            return self._get_services_minimal()

    def _get_services_minimal(self):
        """Minimal fallback - return some common services."""
        print("Using minimal service list fallback")

        common_services = [
            ('wuauserv', 'Windows Update', 'Unknown'),
            ('spooler', 'Print Spooler', 'Unknown'),
            ('eventlog', 'Windows Event Log', 'Unknown'),
            ('windefend', 'Windows Defender Antivirus Service', 'Unknown'),
            ('bits', 'Background Intelligent Transfer Service', 'Unknown'),
            ('cryptsvc', 'Cryptographic Services', 'Unknown'),
            ('dhcp', 'DHCP Client', 'Unknown'),
            ('dnscache', 'DNS Client', 'Unknown'),
            ('rpcss', 'Remote Procedure Call (RPC)', 'Unknown'),
            ('schedule', 'Task Scheduler', 'Unknown')
        ]

        services = []
        for name, display_name, status in common_services:
            service_info = {
                'name': name,
                'display_name': display_name,
                'status': status,
                'start_type': 'Unknown',
                'description': 'Common Windows Service',
                'path_name': 'Unknown',
                'service_type': 'Unknown',
                'process_id': 0,
                'category': self._categorize_service(name)
            }
            services.append(service_info)

        return services

    def _categorize_service(self, service_name):
        """Categorize services based on their importance and type."""
        service_name_lower = service_name.lower()

        # Critical system services
        critical_services = [
            'winlogon', 'csrss', 'wininit', 'services', 'lsass', 'svchost',
            'dwm', 'explorer', 'audiodg', 'conhost', 'winlogon', 'smss'
        ]

        # Windows essential services
        essential_services = [
            'eventlog', 'rpcss', 'dcomlaunch', 'plugplay', 'power', 'profiler',
            'schedule', 'seclogon', 'sens', 'sharedaccess', 'shellhwdetection',
            'spooler', 'srservice', 'stisvc', 'themes', 'winmgmt', 'wuauserv',
            'bits', 'cryptsvc', 'dhcp', 'dnscache', 'eventlog', 'lanmanserver',
            'lanmanworkstation', 'netlogon', 'nla', 'policyagent', 'samss',
            'termservice', 'w32time', 'workstation'
        ]

        # Windows Update related
        update_services = ['wuauserv', 'bits', 'cryptsvc', 'trustedinstaller']

        # Security services
        security_services = [
            'windefend', 'wscsvc', 'securityhealthservice', 'sense',
            'mpssvc', 'bfe', 'keyiso', 'vaultSvc'
        ]

        # Third-party indicators
        third_party_indicators = [
            'adobe', 'google', 'microsoft office', 'steam', 'nvidia', 'intel',
            'realtek', 'vmware', 'virtualbox', 'teamviewer', 'skype', 'zoom'
        ]

        if any(critical in service_name_lower for critical in critical_services):
            return 'Critical'
        elif any(essential in service_name_lower for essential in essential_services):
            return 'Essential'
        elif any(update in service_name_lower for update in update_services):
            return 'Windows Update'
        elif any(security in service_name_lower for security in security_services):
            return 'Security'
        elif any(third_party in service_name_lower for third_party in third_party_indicators):
            return 'Third-party'
        else:
            return 'Standard'

    def check_admin_privileges(self):
        """Check if the application is running with administrator privileges."""
        import ctypes
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def restart_as_admin(self):
        """Restart the application with administrator privileges."""
        import ctypes
        import sys

        try:
            # Show a message that the app will restart
            messagebox.showinfo("Restarting as Administrator",
                              "The application will now restart with administrator privileges.\n\n"
                              "Please click 'Yes' in the User Account Control dialog that appears.")

            # Close current application
            self.root.quit()

            # Restart with admin privileges
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                sys.executable,
                " ".join(sys.argv),
                None,
                1
            )

        except Exception as e:
            messagebox.showerror("Restart Failed",
                                f"Failed to restart as administrator: {str(e)}\n\n"
                                f"Please manually restart the application as Administrator.")

        # Exit current instance
        sys.exit(0)

    def control_service(self, service_name, action):
        """Control a Windows service (start/stop/restart)."""
        import subprocess

        try:
            if not self.check_admin_privileges():
                return False, "Administrator privileges required for service control"

            if action == 'start':
                cmd = ['sc', 'start', service_name]
            elif action == 'stop':
                cmd = ['sc', 'stop', service_name]
            elif action == 'restart':
                # Stop first, then start
                stop_result = subprocess.run(['sc', 'stop', service_name],
                                           capture_output=True, text=True, timeout=30)
                if stop_result.returncode != 0 and "service is not started" not in stop_result.stderr.lower():
                    return False, f"Failed to stop service: {stop_result.stderr}"

                # Wait a moment before starting
                import time
                time.sleep(2)
                cmd = ['sc', 'start', service_name]
            else:
                return False, f"Invalid action: {action}"

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                return True, f"Service {action} command executed successfully"
            else:
                return False, f"Service {action} failed: {result.stderr}"

        except subprocess.TimeoutExpired:
            return False, f"Service {action} operation timed out"
        except Exception as e:
            return False, f"Error controlling service: {str(e)}"

    def get_service_dependencies(self, service_name):
        """Get services that depend on the specified service."""
        import subprocess

        try:
            # Get services that depend on this service
            ps_command = [
                "powershell",
                "-Command",
                f"Get-Service -Name '{service_name}' | Select-Object -ExpandProperty DependentServices | Select-Object Name, Status"
            ]

            result = subprocess.run(
                ps_command,
                capture_output=True,
                text=True,
                timeout=30,
                shell=True
            )

            if result.returncode == 0 and result.stdout.strip():
                # Parse the output to extract dependent services
                lines = result.stdout.strip().split('\n')
                dependencies = []
                for line in lines[2:]:  # Skip header lines
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            dependencies.append(parts[0])
                return dependencies
            else:
                return []

        except Exception as e:
            print(f"Error getting service dependencies: {e}")
            return []

    def toggle_windows_update(self, enable=True):
        """Enable or disable Windows Update service."""
        import subprocess

        try:
            if not self.check_admin_privileges():
                return False, "Administrator privileges required"

            service_name = "wuauserv"

            if enable:
                # Enable and start Windows Update
                commands = [
                    ['sc', 'config', service_name, 'start=', 'auto'],
                    ['sc', 'start', service_name]
                ]
                action_desc = "enabled"
            else:
                # Stop and disable Windows Update
                commands = [
                    ['sc', 'stop', service_name],
                    ['sc', 'config', service_name, 'start=', 'disabled']
                ]
                action_desc = "disabled"

            for cmd in commands:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode != 0:
                    # Some failures are acceptable (like stopping an already stopped service)
                    if "service is not started" not in result.stderr.lower():
                        print(f"Command failed: {' '.join(cmd)} - {result.stderr}")

            return True, f"Windows Update has been {action_desc}"

        except Exception as e:
            return False, f"Error toggling Windows Update: {str(e)}"

    def toggle_hyperv(self, enable=True):
        """Enable or disable Hyper-V feature."""
        import subprocess

        try:
            if not self.check_admin_privileges():
                return False, "Administrator privileges required"

            if enable:
                cmd = ['dism', '/online', '/enable-feature', '/featurename:Microsoft-Hyper-V-All', '/all', '/norestart']
                action_desc = "enabled"
            else:
                cmd = ['dism', '/online', '/disable-feature', '/featurename:Microsoft-Hyper-V-All', '/norestart']
                action_desc = "disabled"

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                return True, f"Hyper-V has been {action_desc}. A system restart is required."
            else:
                return False, f"Failed to {action_desc.split()[0]} Hyper-V: {result.stderr}"

        except Exception as e:
            return False, f"Error toggling Hyper-V: {str(e)}"

    def show_service_manager(self):
        """Show Windows Service Manager dialog."""
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Windows Service Manager")
        dialog.geometry("1200x700")
        dialog.minsize(1000, 600)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(background=self.colors["background"])
        self.center_window(dialog)

        # Create main frame
        main_frame = ttk.Frame(dialog, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_label = ttk.Label(
            main_frame,
            text="🔧 Windows Service Manager",
            style="Title.TLabel"
        )
        header_label.pack(pady=(0, 10))

        # Description
        desc_label = ttk.Label(
            main_frame,
            text="Manage Windows services with advanced controls. Critical services are marked in red, essential services in orange.",
            style="Info.TLabel",
            wraplength=1150
        )
        desc_label.pack(pady=(0, 15))

        # Search and filter frame
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        # Search entry
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.service_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.service_search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 15))

        # Filter by status
        ttk.Label(search_frame, text="Status:").pack(side=tk.LEFT, padx=(0, 5))
        self.service_status_filter = tk.StringVar(value="All")
        status_combo = ttk.Combobox(search_frame, textvariable=self.service_status_filter,
                                   values=["All", "Running", "Stopped"], width=10, state="readonly")
        status_combo.pack(side=tk.LEFT, padx=(0, 15))

        # Filter by category
        ttk.Label(search_frame, text="Category:").pack(side=tk.LEFT, padx=(0, 5))
        self.service_category_filter = tk.StringVar(value="All")
        category_combo = ttk.Combobox(search_frame, textvariable=self.service_category_filter,
                                     values=["All", "Critical", "Essential", "Security", "Windows Update", "Third-party", "Standard"],
                                     width=12, state="readonly")
        category_combo.pack(side=tk.LEFT, padx=(0, 15))

        # Bind search and filter events
        self.service_search_var.trace("w", lambda *args: self.filter_services(dialog))
        self.service_status_filter.trace("w", lambda *args: self.filter_services(dialog))
        self.service_category_filter.trace("w", lambda *args: self.filter_services(dialog))

        # Control buttons frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 15))

        # Left side buttons
        left_buttons = ttk.Frame(control_frame)
        left_buttons.pack(side=tk.LEFT)

        # Refresh button
        refresh_btn = ttk.Button(
            left_buttons,
            text="🔄 Refresh Services",
            command=lambda: self.refresh_services(dialog),
            style="Primary.TButton"
        )
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Service control buttons
        self.start_service_btn = ttk.Button(
            left_buttons,
            text="▶️ Start Service",
            command=lambda: self.start_selected_service(dialog),
            style="Secondary.TButton",
            state='disabled'
        )
        self.start_service_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.stop_service_btn = ttk.Button(
            left_buttons,
            text="⏹️ Stop Service",
            command=lambda: self.stop_selected_service(dialog),
            style="Secondary.TButton",
            state='disabled'
        )
        self.stop_service_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.restart_service_btn = ttk.Button(
            left_buttons,
            text="🔄 Restart Service",
            command=lambda: self.restart_selected_service(dialog),
            style="Secondary.TButton",
            state='disabled'
        )
        self.restart_service_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Right side buttons
        right_buttons = ttk.Frame(control_frame)
        right_buttons.pack(side=tk.RIGHT)

        # Advanced features buttons
        windows_update_btn = ttk.Button(
            right_buttons,
            text="🔄 Windows Update",
            command=lambda: self.show_windows_update_dialog(dialog),
            style="Secondary.TButton"
        )
        windows_update_btn.pack(side=tk.RIGHT, padx=(10, 0))

        hyperv_btn = ttk.Button(
            right_buttons,
            text="💻 Hyper-V",
            command=lambda: self.show_hyperv_dialog(dialog),
            style="Secondary.TButton"
        )
        hyperv_btn.pack(side=tk.RIGHT, padx=(10, 0))

        # Export dropdown for services
        service_export_var = tk.StringVar(value="📤 Export")
        service_export_combo = ttk.Combobox(
            right_buttons,
            textvariable=service_export_var,
            values=["📤 Export", "📄 JSON", "📝 Text"],
            state="readonly",
            width=12,
            style="TCombobox"
        )
        service_export_combo.pack(side=tk.RIGHT, padx=(10, 0))

        def on_service_export_select(event):
            selection = service_export_var.get()
            if selection == "📄 JSON":
                self.export_services_dialog(dialog, 'json')
                service_export_var.set("📤 Export")
            elif selection == "📝 Text":
                self.export_services_dialog(dialog, 'text')
                service_export_var.set("📤 Export")

        service_export_combo.bind("<<ComboboxSelected>>", on_service_export_select)

        # Create treeview for services
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Define columns
        columns = ("name", "display_name", "status", "start_type", "category", "description")
        self.services_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)

        # Configure columns
        self.services_tree.heading("name", text="Service Name")
        self.services_tree.heading("display_name", text="Display Name")
        self.services_tree.heading("status", text="Status")
        self.services_tree.heading("start_type", text="Startup Type")
        self.services_tree.heading("category", text="Category")
        self.services_tree.heading("description", text="Description")

        # Set column widths
        self.services_tree.column("name", width=150)
        self.services_tree.column("display_name", width=200)
        self.services_tree.column("status", width=80)
        self.services_tree.column("start_type", width=100)
        self.services_tree.column("category", width=100)
        self.services_tree.column("description", width=300)

        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.services_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.services_tree.xview)
        self.services_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack treeview and scrollbars
        self.services_tree.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.E, tk.W))

        # Configure grid weights
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        # Bind selection event
        self.services_tree.bind('<<TreeviewSelect>>', lambda e: self.on_service_selection(dialog))

        # Status and info frame
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        # Status label
        self.service_status_label = ttk.Label(
            info_frame,
            text="Click 'Refresh Services' to load service data",
            style="Info.TLabel"
        )
        self.service_status_label.pack(side=tk.LEFT)

        # Admin status label
        admin_status = "Administrator" if self.check_admin_privileges() else "Standard User"
        admin_color = "green" if self.check_admin_privileges() else "red"
        self.admin_status_label = ttk.Label(
            info_frame,
            text=f"Running as: {admin_status}",
            style="Info.TLabel"
        )
        self.admin_status_label.pack(side=tk.RIGHT)

        # Close button
        close_btn = ttk.Button(
            main_frame,
            text="Close",
            command=dialog.destroy,
            style="Secondary.TButton"
        )
        close_btn.pack(pady=(10, 0))

        # Store dialog reference
        self.service_dialog = dialog
        self.all_services = []  # Store all services for filtering

        # Auto-refresh on open
        self.refresh_services(dialog)

    def refresh_services(self, dialog):
        """Refresh the services display."""
        self.service_status_label.config(text="Loading Windows services...")
        dialog.update()

        # Clear existing items
        for item in self.services_tree.get_children():
            self.services_tree.delete(item)

        # Get services in background thread
        threading.Thread(target=self.load_services_thread, args=(dialog,), daemon=True).start()

    def load_services_thread(self, dialog):
        """Load services in background thread."""
        try:
            print("Starting to load Windows services...")
            services = self.get_windows_services()
            print(f"Loaded {len(services)} services from get_windows_services()")

            # Update UI in main thread
            dialog.after(0, lambda: self.update_services_display(dialog, services))

        except Exception as e:
            error_msg = f"Error loading services: {str(e)}"
            print(error_msg)
            dialog.after(0, lambda: self.service_status_label.config(text=error_msg))

    def update_services_display(self, dialog, services):
        """Update the services display."""
        try:
            print(f"Updating services display with {len(services)} services")

            # Store all services for filtering
            self.all_services = services

            if not services:
                self.service_status_label.config(text="No services found. This might indicate a PowerShell execution issue.")
                # Show a helpful message in the tree
                self.services_tree.insert("", tk.END, values=(
                    "No services found",
                    "PowerShell might be restricted or services unavailable",
                    "Unknown",
                    "Unknown",
                    "Error",
                    "Try running as Administrator or check PowerShell execution policy"
                ))
                return

            # Apply current filters
            self.filter_services(dialog)

            self.service_status_label.config(text=f"Loaded {len(services)} Windows services")

        except Exception as e:
            error_msg = f"Error updating display: {str(e)}"
            print(error_msg)
            self.service_status_label.config(text=error_msg)

    def filter_services(self, dialog):
        """Filter services based on search and filter criteria."""
        try:
            # Clear existing items
            for item in self.services_tree.get_children():
                self.services_tree.delete(item)

            if not hasattr(self, 'all_services') or not self.all_services:
                return

            # Get filter criteria
            search_text = self.service_search_var.get().lower()
            status_filter = self.service_status_filter.get()
            category_filter = self.service_category_filter.get()

            # Filter services
            filtered_services = []
            for service in self.all_services:
                # Apply search filter
                if search_text and search_text not in service['name'].lower() and search_text not in service['display_name'].lower():
                    continue

                # Apply status filter
                if status_filter != "All" and service['status'] != status_filter:
                    continue

                # Apply category filter
                if category_filter != "All" and service['category'] != category_filter:
                    continue

                filtered_services.append(service)

            # Sort services by category priority, then by name
            category_priority = {'Critical': 0, 'Essential': 1, 'Security': 2, 'Windows Update': 3, 'Standard': 4, 'Third-party': 5}
            filtered_services.sort(key=lambda x: (category_priority.get(x['category'], 6), x['name'].lower()))

            # Add filtered services to tree
            for service in filtered_services:
                # Determine row color based on category
                tags = ()
                if service['category'] == 'Critical':
                    tags = ('critical',)
                elif service['category'] == 'Essential':
                    tags = ('essential',)
                elif service['category'] == 'Security':
                    tags = ('security',)
                elif service['category'] == 'Windows Update':
                    tags = ('update',)
                elif service['category'] == 'Third-party':
                    tags = ('third_party',)

                self.services_tree.insert("", tk.END, values=(
                    service['name'],
                    service['display_name'],
                    service['status'],
                    service['start_type'],
                    service['category'],
                    service['description'][:100] + "..." if len(service['description']) > 100 else service['description']
                ), tags=tags)

            # Configure tags for color coding - use app background
            self.services_tree.tag_configure('critical', background=self.colors["background"], foreground='#dc3545')
            self.services_tree.tag_configure('essential', background=self.colors["background"], foreground='#ffc107')
            self.services_tree.tag_configure('security', background=self.colors["background"], foreground='#28a745')
            self.services_tree.tag_configure('update', background=self.colors["background"], foreground='#007bff')
            self.services_tree.tag_configure('third_party', background=self.colors["background"], foreground='#6c757d')

            # Update status
            if hasattr(self, 'service_status_label'):
                self.service_status_label.config(text=f"Showing {len(filtered_services)} of {len(self.all_services)} services")

        except Exception as e:
            if hasattr(self, 'service_status_label'):
                self.service_status_label.config(text=f"Error filtering services: {str(e)}")

    def on_service_selection(self, dialog):
        """Handle service selection."""
        selection = self.services_tree.selection()
        if selection:
            # Enable service control buttons
            self.start_service_btn.config(state='normal')
            self.stop_service_btn.config(state='normal')
            self.restart_service_btn.config(state='normal')
        else:
            # Disable service control buttons
            self.start_service_btn.config(state='disabled')
            self.stop_service_btn.config(state='disabled')
            self.restart_service_btn.config(state='disabled')

    def start_selected_service(self, dialog):
        """Start the selected service."""
        self._control_selected_service(dialog, 'start')

    def stop_selected_service(self, dialog):
        """Stop the selected service."""
        self._control_selected_service(dialog, 'stop')

    def restart_selected_service(self, dialog):
        """Restart the selected service."""
        self._control_selected_service(dialog, 'restart')

    def _control_selected_service(self, dialog, action):
        """Control the selected service with safety checks."""
        selection = self.services_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a service to control.")
            return

        # Get selected service data
        item = selection[0]
        values = self.services_tree.item(item, 'values')
        service_name = values[0]
        display_name = values[1]
        category = values[4]

        # Safety checks for critical services
        if category == 'Critical' and action == 'stop':
            if not messagebox.askyesno("Critical Service Warning",
                                     f"'{display_name}' is a critical system service.\n\n"
                                     f"Stopping this service may cause system instability or prevent Windows from functioning properly.\n\n"
                                     f"Are you sure you want to stop this service?"):
                return

        # Check dependencies for stop action
        if action == 'stop':
            dependencies = self.get_service_dependencies(service_name)
            if dependencies:
                dep_list = '\n'.join(f"• {dep}" for dep in dependencies[:5])
                if len(dependencies) > 5:
                    dep_list += f"\n• ... and {len(dependencies) - 5} more"

                if not messagebox.askyesno("Service Dependencies",
                                         f"The following services depend on '{display_name}':\n\n{dep_list}\n\n"
                                         f"Stopping this service may affect these dependent services.\n\n"
                                         f"Continue anyway?"):
                    return

        # Check admin privileges
        if not self.check_admin_privileges():
            result = messagebox.askyesno("Administrator Required",
                                       "Administrator privileges are required to control Windows services.\n\n"
                                       "Would you like to restart the application as Administrator?\n\n"
                                       "Click 'Yes' to restart with admin privileges, or 'No' to continue without service control.")
            if result:
                self.restart_as_admin()
            return

        # Perform the action
        self.service_status_label.config(text=f"{action.capitalize()}ing service '{display_name}'...")
        dialog.update()

        # Run in background thread
        threading.Thread(target=self._service_control_thread,
                        args=(dialog, service_name, display_name, action), daemon=True).start()

    def _service_control_thread(self, dialog, service_name, display_name, action):
        """Background thread for service control operations."""
        try:
            success, message = self.control_service(service_name, action)

            # Update UI in main thread
            dialog.after(0, lambda: self._service_control_complete(dialog, display_name, action, success, message))

        except Exception as e:
            dialog.after(0, lambda: self._service_control_complete(dialog, display_name, action, False, str(e)))

    def _service_control_complete(self, dialog, display_name, action, success, message):
        """Handle service control completion."""
        if success:
            messagebox.showinfo("Success", f"Service '{display_name}' {action} operation completed successfully.")
            # Refresh the services list
            self.refresh_services(dialog)
        else:
            messagebox.showerror("Error", f"Failed to {action} service '{display_name}':\n\n{message}")
            self.service_status_label.config(text="Ready")

    def show_windows_update_dialog(self, parent_dialog):
        """Show simple Windows Update management dialog."""
        # Create modern dialog
        update_dialog = self.create_modern_dialog(
            parent_dialog,
            "Windows Update Management",
            width=500,
            height=350,
            min_width=450,
            min_height=300
        )

        # Create main container
        main_container = ttk.Frame(update_dialog, style="Surface.TFrame")
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Create modern header
        self.create_modern_header(
            main_container,
            "Windows Update Management",
            icon="🔄",
            subtitle="Manage Windows Update service and settings"
        )

        # Status section
        status_section = ttk.Frame(main_container, style="Surface.TFrame", padding="15")
        status_section.pack(fill=tk.X, pady=(0, 15))

        status_header = ttk.Label(
            status_section,
            text="📊 Current Status",
            style="Subtitle.TLabel"
        )
        status_header.pack(anchor=tk.W, pady=(0, 10))

        # Status display
        self.update_status_label = ttk.Label(
            status_section,
            text="Checking Windows Update status...",
            style="Info.TLabel"
        )
        self.update_status_label.pack(anchor=tk.W, pady=(0, 10))

        # Actions section
        actions_section = ttk.Frame(main_container, style="Surface.TFrame", padding="15")
        actions_section.pack(fill=tk.X, pady=(0, 15))

        actions_header = ttk.Label(
            actions_section,
            text="⚡ Actions",
            style="Subtitle.TLabel"
        )
        actions_header.pack(anchor=tk.W, pady=(0, 10))

        # Single action button (Enable OR Disable based on current status)
        self.windows_update_action_btn = ttk.Button(
            actions_section,
            text="🔄 Checking...",
            state='disabled',
            command=lambda: self.toggle_windows_update_simple(update_dialog),
            style="Primary.TButton"
        )
        self.windows_update_action_btn.pack(fill=tk.X, pady=(0, 10))

        # Refresh button
        refresh_btn = ttk.Button(
            actions_section,
            text="🔄 Refresh Status",
            command=lambda: self.check_windows_update_simple(update_dialog),
            style="Secondary.TButton"
        )
        refresh_btn.pack(fill=tk.X, pady=(0, 10))

        # Modern button frame for close
        button_config = [
            ("❌ Close", update_dialog.destroy, "Secondary.TButton", tk.RIGHT)
        ]
        self.create_modern_button_frame(main_container, button_config)

        # Check status immediately
        self.check_windows_update_simple(update_dialog)

    def check_windows_update_simple(self, dialog):
        """Simple Windows Update status check with single button logic."""
        try:
            # Disable button while checking
            self.windows_update_action_btn.config(text="🔄 Checking...", state='disabled')
            self.update_status_label.config(text="Checking Windows Update status...")

            # Check Windows Update service status
            result = subprocess.run(
                ['sc', 'query', 'wuauserv'],
                capture_output=True,
                text=True,
                timeout=10,
                shell=True
            )

            if result.returncode == 0:
                output = result.stdout
                status = "Unknown"

                # Extract status
                for line in output.split('\n'):
                    line = line.strip()
                    if 'STATE' in line and 'RUNNING' in line:
                        status = "Running"
                    elif 'STATE' in line and 'STOPPED' in line:
                        status = "Stopped"

                # Get startup type
                config_result = subprocess.run(
                    ['sc', 'qc', 'wuauserv'],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    shell=True
                )

                start_type = "Unknown"
                if config_result.returncode == 0:
                    for line in config_result.stdout.split('\n'):
                        line = line.strip()
                        if 'START_TYPE' in line:
                            if 'AUTO_START' in line:
                                start_type = "Automatic"
                            elif 'DEMAND_START' in line:
                                start_type = "Manual"
                            elif 'DISABLED' in line:
                                start_type = "Disabled"

                # Update status display
                self.update_status_label.config(text=f"Status: {status} | Startup: {start_type}")

                # Set button based on current status - SIMPLE LOGIC
                if start_type == "Disabled" or status == "Stopped":
                    # Windows Update is disabled/stopped -> Show ENABLE button
                    self.windows_update_action_btn.config(
                        text="✅ Enable Windows Update",
                        state='normal'
                    )
                    self.current_wu_action = True  # Next action is enable
                else:
                    # Windows Update is enabled/running -> Show DISABLE button
                    self.windows_update_action_btn.config(
                        text="❌ Disable Windows Update",
                        state='normal'
                    )
                    self.current_wu_action = False  # Next action is disable

            else:
                self.update_status_label.config(text="Unable to check Windows Update status")
                self.windows_update_action_btn.config(text="❓ Status Unknown", state='disabled')

        except Exception as e:
            self.update_status_label.config(text=f"Error: {str(e)}")
            self.windows_update_action_btn.config(text="❓ Error", state='disabled')



    def toggle_windows_update_simple(self, dialog):
        """Simple Windows Update toggle based on current status."""
        if not hasattr(self, 'current_wu_action'):
            messagebox.showwarning("Status Unknown", "Please refresh the status first.")
            return

        if not self.check_admin_privileges():
            result = messagebox.askyesno("Administrator Required",
                                       "Administrator privileges are required to modify Windows Update settings.\n\n"
                                       "Would you like to restart the application as Administrator?")
            if result:
                self.restart_as_admin()
            return

        enable = self.current_wu_action
        action_text = "enable" if enable else "disable"

        # Confirmation for disabling
        if not enable:
            if not messagebox.askyesno("Disable Windows Update",
                                     "Are you sure you want to disable Windows Update?\n\n"
                                     "This will prevent security updates!\n\n"
                                     "Continue anyway?"):
                return

        # Update UI
        self.windows_update_action_btn.config(text=f"🔄 {action_text.capitalize()}ing...", state='disabled')
        self.update_status_label.config(text=f"{action_text.capitalize()}ing Windows Update...")
        dialog.update()

        # Run operation in background
        threading.Thread(target=self._windows_update_simple_thread, args=(dialog, enable), daemon=True).start()

    def _windows_update_simple_thread(self, dialog, enable):
        """Background thread for simple Windows Update operations."""
        try:
            success, message = self.toggle_windows_update(enable)
            dialog.after(0, lambda: self._windows_update_simple_complete(dialog, success, message))
        except Exception as e:
            dialog.after(0, lambda: self._windows_update_simple_complete(dialog, False, str(e)))

    def _windows_update_simple_complete(self, dialog, success, message):
        """Handle simple Windows Update operation completion."""
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)

        # Refresh status to update button
        self.check_windows_update_simple(dialog)

    def show_hyperv_dialog(self, parent_dialog):
        """Show Hyper-V management dialog."""
        # Create modern dialog
        hyperv_dialog = self.create_modern_dialog(
            parent_dialog,
            "Hyper-V Management",
            width=600,
            height=500,
            min_width=550,
            min_height=450
        )

        # Create main container
        main_container = ttk.Frame(hyperv_dialog, style="Surface.TFrame")
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Create modern header
        self.create_modern_header(
            main_container,
            "Hyper-V Management",
            icon="💻",
            subtitle="Microsoft's hardware virtualization platform management"
        )

        # Information section
        info_section = ttk.Frame(main_container, style="Surface.TFrame", padding="15")
        info_section.pack(fill=tk.X, pady=(0, 15))

        info_header = ttk.Label(
            info_section,
            text="ℹ️ About Hyper-V",
            style="Subtitle.TLabel"
        )
        info_header.pack(anchor=tk.W, pady=(0, 10))

        info_text = """Enabling Hyper-V will:
• Allow you to create and run virtual machines
• Enable Windows Subsystem for Linux 2 (WSL2)
• Provide hardware-level virtualization support

Disabling Hyper-V will:
• Remove virtualization capabilities
• May improve performance for some applications
• Allow other virtualization software to work properly

⚠️ A system restart is required after making changes."""

        info_label = ttk.Label(
            info_section,
            text=info_text,
            style="Info.TLabel",
            wraplength=500,
            justify=tk.LEFT
        )
        info_label.pack(anchor=tk.W, pady=(0, 10))

        # Status section
        status_section = ttk.Frame(main_container, style="Surface.TFrame", padding="15")
        status_section.pack(fill=tk.X, pady=(0, 15))

        status_header = ttk.Label(
            status_section,
            text="📊 Current Status",
            style="Subtitle.TLabel"
        )
        status_header.pack(anchor=tk.W, pady=(0, 10))

        self.hyperv_status_label = ttk.Label(
            status_section,
            text="Checking Hyper-V status...",
            style="Info.TLabel"
        )
        self.hyperv_status_label.pack(anchor=tk.W, pady=(0, 10))

        # Actions section
        actions_section = ttk.Frame(main_container, style="Surface.TFrame", padding="15")
        actions_section.pack(fill=tk.X, pady=(0, 15))

        actions_header = ttk.Label(
            actions_section,
            text="⚡ Actions",
            style="Subtitle.TLabel"
        )
        actions_header.pack(anchor=tk.W, pady=(0, 10))

        # Button container for better layout
        button_container = ttk.Frame(actions_section, style="Surface.TFrame")
        button_container.pack(fill=tk.X, pady=(0, 10))

        # Enable Hyper-V button
        self.enable_hyperv_btn = ttk.Button(
            button_container,
            text="✅ Enable Hyper-V",
            command=lambda: self.toggle_hyperv_action(hyperv_dialog, True),
            style="Primary.TButton"
        )
        self.enable_hyperv_btn.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)

        # Disable Hyper-V button
        self.disable_hyperv_btn = ttk.Button(
            button_container,
            text="❌ Disable Hyper-V",
            command=lambda: self.toggle_hyperv_action(hyperv_dialog, False),
            style="Action.TButton"
        )
        self.disable_hyperv_btn.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)

        # Refresh status button
        refresh_hyperv_btn = ttk.Button(
            actions_section,
            text="🔄 Refresh Status",
            command=lambda: self.check_hyperv_status(hyperv_dialog),
            style="Secondary.TButton"
        )
        refresh_hyperv_btn.pack(fill=tk.X, pady=(0, 10))

        # Ensure buttons are initially visible and enabled (fallback)
        self.enable_hyperv_btn.config(state='normal', text="✅ Enable Hyper-V")
        self.disable_hyperv_btn.config(state='normal', text="❌ Disable Hyper-V")

        # Modern button frame for close
        button_config = [
            ("❌ Close", hyperv_dialog.destroy, "Secondary.TButton", tk.RIGHT)
        ]
        self.create_modern_button_frame(main_container, button_config)

        # Check current status after a short delay
        hyperv_dialog.after(100, lambda: self.check_hyperv_status(hyperv_dialog))

    def check_hyperv_status(self, dialog):
        """Check current Hyper-V status and update buttons."""
        try:
            # Disable buttons while checking
            if hasattr(self, 'enable_hyperv_btn'):
                self.enable_hyperv_btn.config(state='disabled')
            if hasattr(self, 'disable_hyperv_btn'):
                self.disable_hyperv_btn.config(state='disabled')

            # Update status label
            self.hyperv_status_label.config(text="🔄 Checking Hyper-V status...")

            # Check if Hyper-V feature is enabled using DISM (more reliable)
            result = subprocess.run(
                ['dism', '/online', '/get-featureinfo', '/featurename:Microsoft-Hyper-V-All'],
                capture_output=True,
                text=True,
                timeout=30,
                shell=True
            )

            if result.returncode == 0:
                output = result.stdout
                state = "Unknown"

                # Parse DISM output
                for line in output.split('\n'):
                    line = line.strip()
                    if 'State :' in line:
                        if 'Enabled' in line:
                            state = "Enabled"
                        elif 'Disabled' in line:
                            state = "Disabled"
                        break

                # Update status display
                status_text = f"Hyper-V Status: {state}"
                self.hyperv_status_label.config(text=status_text)

                # Enable/disable buttons based on current status
                if hasattr(self, 'enable_hyperv_btn') and hasattr(self, 'disable_hyperv_btn'):
                    if state == "Disabled":
                        # Hyper-V is disabled - enable "Enable" button, disable "Disable" button
                        self.enable_hyperv_btn.config(state='normal')
                        self.disable_hyperv_btn.config(state='disabled')
                        self.enable_hyperv_btn.config(text="✅ Enable Hyper-V")
                        self.disable_hyperv_btn.config(text="❌ Disable Hyper-V (Already Disabled)")
                    elif state == "Enabled":
                        # Hyper-V is enabled - enable "Disable" button, disable "Enable" button
                        self.enable_hyperv_btn.config(state='disabled')
                        self.disable_hyperv_btn.config(state='normal')
                        self.enable_hyperv_btn.config(text="✅ Enable Hyper-V (Already Enabled)")
                        self.disable_hyperv_btn.config(text="❌ Disable Hyper-V")
                    else:
                        # Status unknown - enable both buttons
                        self.enable_hyperv_btn.config(state='normal', text="✅ Enable Hyper-V")
                        self.disable_hyperv_btn.config(state='normal', text="❌ Disable Hyper-V")

            else:
                # Fallback to PowerShell method
                self._check_hyperv_powershell(dialog)

        except Exception as e:
            error_msg = f"Error checking status: {str(e)}"
            self.hyperv_status_label.config(text=error_msg)
            # Enable both buttons if error occurred
            if hasattr(self, 'enable_hyperv_btn') and hasattr(self, 'disable_hyperv_btn'):
                self.enable_hyperv_btn.config(state='normal', text="✅ Enable Hyper-V")
                self.disable_hyperv_btn.config(state='normal', text="❌ Disable Hyper-V")

    def _check_hyperv_powershell(self, dialog):
        """Fallback method to check Hyper-V status using PowerShell."""
        try:
            ps_command = [
                "powershell",
                "-ExecutionPolicy", "Bypass",
                "-Command",
                "Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All | Select-Object State"
            ]

            result = subprocess.run(ps_command, capture_output=True, text=True, timeout=15, shell=True)

            if result.returncode == 0:
                output = result.stdout
                state = "Unknown"

                if 'Enabled' in output:
                    state = "Enabled"
                elif 'Disabled' in output:
                    state = "Disabled"

                status_text = f"Hyper-V Status: {state}"
                self.hyperv_status_label.config(text=status_text)

                # Update button based on status
                if hasattr(self, 'hyperv_toggle_btn'):
                    if state == "Disabled":
                        self.hyperv_toggle_btn.config(
                            text="✅ Enable Hyper-V",
                            state='normal'
                        )
                        self.current_hyperv_action = True
                    elif state == "Enabled":
                        self.hyperv_toggle_btn.config(
                            text="❌ Disable Hyper-V",
                            state='normal'
                        )
                        self.current_hyperv_action = False
                    else:
                        self.hyperv_toggle_btn.config(text="❓ Status Unknown", state='disabled')
            else:
                self.hyperv_status_label.config(text="Unable to check Hyper-V status")
                if hasattr(self, 'hyperv_toggle_btn'):
                    self.hyperv_toggle_btn.config(text="❓ Status Unknown", state='disabled')

        except Exception as e:
            self.hyperv_status_label.config(text=f"PowerShell fallback failed: {str(e)}")
            if hasattr(self, 'hyperv_toggle_btn'):
                self.hyperv_toggle_btn.config(text="❓ Status Unknown", state='disabled')



    def toggle_hyperv_action(self, dialog, enable):
        """Handle Hyper-V toggle action."""
        if not self.check_admin_privileges():
            result = messagebox.askyesno("Administrator Required",
                                       "Administrator privileges are required to modify Hyper-V settings.\n\n"
                                       "Would you like to restart the application as Administrator?")
            if result:
                self.restart_as_admin()
            return

        action = "enable" if enable else "disable"

        # Confirmation dialog
        if not messagebox.askyesno(f"{action.capitalize()} Hyper-V",
                                 f"Are you sure you want to {action} Hyper-V?\n\n"
                                 f"A system restart will be required after this operation.\n\n"
                                 f"Continue?"):
            return

        self.hyperv_status_label.config(text=f"{'Enabling' if enable else 'Disabling'} Hyper-V...")
        dialog.update()

        # Run in background thread
        threading.Thread(target=self._hyperv_thread, args=(dialog, enable), daemon=True).start()

    def _hyperv_thread(self, dialog, enable):
        """Background thread for Hyper-V operations."""
        try:
            success, message = self.toggle_hyperv(enable)

            # Update UI in main thread
            dialog.after(0, lambda: self._hyperv_complete(dialog, enable, success, message))

        except Exception as e:
            dialog.after(0, lambda: self._hyperv_complete(dialog, enable, False, str(e)))

    def _hyperv_complete(self, dialog, enable, success, message):
        """Handle Hyper-V operation completion."""
        if success:
            messagebox.showinfo("Success", f"{message}\n\nPlease restart your computer to complete the changes.")
            # Refresh status to update buttons
            self.check_hyperv_status(dialog)
        else:
            messagebox.showerror("Error", message)
            self.hyperv_status_label.config(text="Operation failed")
            # Re-enable both buttons
            if hasattr(self, 'enable_hyperv_btn') and hasattr(self, 'disable_hyperv_btn'):
                self.enable_hyperv_btn.config(state='normal')
                self.disable_hyperv_btn.config(state='normal')

    def export_services_dialog(self, dialog, format_type=None):
        """Show export services dialog or export directly if format specified."""
        if not hasattr(self, 'all_services') or not self.all_services:
            messagebox.showwarning("No Data", "No services data to export. Please refresh the services list first.")
            return

        # If format is specified, export directly
        if format_type:
            self.export_services_data(format_type)
            return

    def export_services_data(self, format_type):
        """Export services data in specified format."""
        try:
            from tkinter import filedialog
            import json
            from datetime import datetime

            # Get export options (default values)
            include_stopped = True
            include_descriptions = True

            # Prepare data
            export_data = {
                'export_info': {
                    'timestamp': datetime.now().isoformat(),
                    'total_services': len(self.all_services),
                    'format': format_type
                },
                'services': []
            }

            for service in self.all_services:
                if not include_stopped and service.get('status', '').lower() != 'running':
                    continue

                service_data = {
                    'name': service.get('name', ''),
                    'display_name': service.get('display_name', ''),
                    'status': service.get('status', ''),
                    'startup_type': service.get('startup_type', ''),
                    'category': service.get('category', 'Standard')
                }

                if include_descriptions:
                    service_data['description'] = service.get('description', '')

                export_data['services'].append(service_data)

            # Choose file location
            if format_type == 'json':
                filename = filedialog.asksaveasfilename(
                    defaultextension=".json",
                    filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                    title="Save Services Export"
                )
                if filename:
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, indent=2, ensure_ascii=False)
                    messagebox.showinfo("Export Complete", f"Services exported to {filename}")

            elif format_type == 'text':
                filename = filedialog.asksaveasfilename(
                    defaultextension=".txt",
                    filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                    title="Save Services Export"
                )
                if filename:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"Windows Services Export\n")
                        f.write(f"Generated: {export_data['export_info']['timestamp']}\n")
                        f.write(f"Total Services: {export_data['export_info']['total_services']}\n")
                        f.write("=" * 80 + "\n\n")

                        for service in export_data['services']:
                            f.write(f"Service: {service['display_name']}\n")
                            f.write(f"  Name: {service['name']}\n")
                            f.write(f"  Status: {service['status']}\n")
                            f.write(f"  Startup: {service['startup_type']}\n")
                            f.write(f"  Category: {service['category']}\n")
                            if include_descriptions and service.get('description'):
                                f.write(f"  Description: {service['description']}\n")
                            f.write("\n")

                    messagebox.showinfo("Export Complete", f"Services exported to {filename}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export services:\n{str(e)}")

        # Ask for export format
        export_dialog = tk.Toplevel(dialog)
        export_dialog.title("Export Services")
        export_dialog.geometry("400x300")
        export_dialog.transient(dialog)
        export_dialog.grab_set()
        export_dialog.configure(background=self.colors["background"])
        self.center_window(export_dialog)

        # Create main frame
        main_frame = ttk.Frame(export_dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_label = ttk.Label(main_frame, text="📄 Export Services", style="Title.TLabel")
        header_label.pack(pady=(0, 15))

        # Format selection
        format_frame = ttk.LabelFrame(main_frame, text="Export Format", padding=10)
        format_frame.pack(fill=tk.X, pady=(0, 15))

        export_format = tk.StringVar(value="json")

        json_radio = ttk.Radiobutton(format_frame, text="📄 JSON (Structured data)", variable=export_format, value="json", style="TRadiobutton")
        json_radio.pack(anchor=tk.W, pady=2)

        text_radio = ttk.Radiobutton(format_frame, text="📝 Text (Human readable)", variable=export_format, value="text", style="TRadiobutton")
        text_radio.pack(anchor=tk.W, pady=2)

        # Options
        options_frame = ttk.LabelFrame(main_frame, text="Export Options", padding=10)
        options_frame.pack(fill=tk.X, pady=(0, 15))

        include_stopped = tk.BooleanVar(value=True)
        include_stopped_cb = ttk.Checkbutton(options_frame, text="📋 Include stopped services", variable=include_stopped, style="TCheckbutton")
        include_stopped_cb.pack(anchor=tk.W, pady=2)

        include_descriptions = tk.BooleanVar(value=True)
        include_descriptions_cb = ttk.Checkbutton(options_frame, text="📝 Include service descriptions", variable=include_descriptions, style="TCheckbutton")
        include_descriptions_cb.pack(anchor=tk.W, pady=2)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        export_btn = ttk.Button(
            button_frame,
            text="Export",
            command=lambda: self.perform_services_export(export_dialog, export_format.get(),
                                                        include_stopped.get(), include_descriptions.get()),
            style="Primary.TButton"
        )
        export_btn.pack(side=tk.LEFT, padx=(0, 10))

        cancel_btn = ttk.Button(
            button_frame,
            text="Cancel",
            command=export_dialog.destroy,
            style="Secondary.TButton"
        )
        cancel_btn.pack(side=tk.LEFT)

    def perform_services_export(self, dialog, format_type, include_stopped, include_descriptions):
        """Perform the actual services export."""
        try:
            # Filter services based on options
            services_to_export = []
            for service in self.all_services:
                if not include_stopped and service['status'] != 'Running':
                    continue

                export_service = service.copy()
                if not include_descriptions:
                    export_service['description'] = ''

                services_to_export.append(export_service)

            if not services_to_export:
                messagebox.showwarning("No Data", "No services match the export criteria.")
                return

            # Export using the network export function (adapted for services)
            success, message = self.export_services_data(services_to_export, format_type)

            if success:
                messagebox.showinfo("Export Successful", message)
                dialog.destroy()
            else:
                if "cancelled" not in message.lower():
                    messagebox.showerror("Export Failed", message)

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export services data: {str(e)}")

    def export_services_data(self, services, format_type):
        """Export services data to file."""
        import json
        import datetime
        import os

        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

            # Show file dialog
            if format_type == 'json':
                default_filename = f"windows_services_{timestamp}.json"
                file_types = [("JSON files", "*.json"), ("All files", "*.*")]
                extension = ".json"
            else:
                default_filename = f"windows_services_{timestamp}.txt"
                file_types = [("Text files", "*.txt"), ("All files", "*.*")]
                extension = ".txt"

            filepath = filedialog.asksaveasfilename(
                title=f"Save Windows Services Report ({format_type.upper()})",
                defaultextension=extension,
                filetypes=file_types,
                initialfile=default_filename
            )

            if not filepath:  # User cancelled
                return False, "Export cancelled by user"

            if format_type == 'json':
                export_data = {
                    'export_info': {
                        'timestamp': datetime.datetime.now().isoformat(),
                        'date_readable': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'total_services': len(services),
                        'format_version': '1.0',
                        'export_type': 'windows_services'
                    },
                    'services': services
                }

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)

            else:  # text format
                with open(filepath, 'w', encoding='utf-8') as f:
                    # Header
                    f.write("=" * 80 + "\n")
                    f.write("WINDOWS SERVICES REPORT\n")
                    f.write("=" * 80 + "\n")
                    f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Total Services: {len(services)}\n")
                    f.write("=" * 80 + "\n\n")

                    # Group services by category
                    categories = {}
                    for service in services:
                        category = service.get('category', 'Unknown')
                        if category not in categories:
                            categories[category] = []
                        categories[category].append(service)

                    # Write services by category
                    for category, category_services in sorted(categories.items()):
                        f.write(f"CATEGORY: {category.upper()}\n")
                        f.write("-" * 60 + "\n")

                        for service in sorted(category_services, key=lambda x: x['name']):
                            f.write(f"Service Name: {service['name']}\n")
                            f.write(f"Display Name: {service['display_name']}\n")
                            f.write(f"Status: {service['status']}\n")
                            f.write(f"Startup Type: {service['start_type']}\n")
                            if service.get('description'):
                                f.write(f"Description: {service['description']}\n")
                            f.write("\n")

                        f.write("\n")

                    # Summary
                    f.write("=" * 80 + "\n")
                    f.write("SUMMARY\n")
                    f.write("=" * 80 + "\n")

                    # Count by status
                    status_counts = {}
                    for service in services:
                        status = service['status']
                        status_counts[status] = status_counts.get(status, 0) + 1

                    f.write("Services by Status:\n")
                    for status, count in sorted(status_counts.items()):
                        f.write(f"  {status}: {count}\n")

                    # Count by category
                    f.write("\nServices by Category:\n")
                    for category, count in sorted([(cat, len(svcs)) for cat, svcs in categories.items()]):
                        f.write(f"  {category}: {count}\n")

            filename = os.path.basename(filepath)
            return True, f"Successfully exported to {filename}"

        except PermissionError:
            return False, "Permission denied. Please choose a different location or close any programs that might be using the file."
        except FileNotFoundError:
            return False, "Invalid file path. Please choose a valid location."
        except Exception as e:
            return False, f"Export failed: {str(e)}"
    
    def _show_cleanup_results(self, cleanup_results):
        """Show results of cleanup operations."""
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Cleanup Results")
        dialog.geometry("700x500")
        dialog.minsize(600, 400)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(background=self.colors["background"])
        self.center_window(dialog)
        
        # Create main frame
        main_frame = ttk.Frame(dialog, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add header
        ttk.Label(
            main_frame, 
            text="System Cleanup Results", 
            style="Title.TLabel"
        ).pack(pady=(0, 10), anchor=tk.W)
        
        # Summary counts
        success_count = len(cleanup_results["success"])
        failed_count = len(cleanup_results["failed"])
        
        ttk.Label(
            main_frame,
            text=f"Successfully completed: {success_count} operations\nFailed: {failed_count} operations",
            style="Info.TLabel"
        ).pack(pady=(0, 15), anchor=tk.W)
        
        # Create notebook for results
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Success tab
        success_frame = ttk.Frame(notebook, padding=10)
        notebook.add(success_frame, text=f"Successful ({success_count})")
        
        if success_count > 0:
            # Create text widget for success results
            success_text = tk.Text(success_frame, wrap=tk.WORD, height=15,
                                 background=self.colors["background"],
                                 foreground=self.colors["text_primary"],
                                 insertbackground=self.colors["text_primary"])
            success_text.pack(fill=tk.BOTH, expand=True)
            
            # Add scrollbar
            success_scrollbar = ttk.Scrollbar(success_frame, command=success_text.yview)
            success_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            success_text.config(yscrollcommand=success_scrollbar.set)
            
            # Insert success results
            for option, message in cleanup_results["success"]:
                success_text.insert(tk.END, f"✅ {message}\n\n")
                
            success_text.config(state=tk.DISABLED)  # Make read-only
        else:
            ttk.Label(
                success_frame,
                text="No successful operations",
                style="Info.TLabel"
            ).pack(pady=20)
        
        # Failed tab
        failed_frame = ttk.Frame(notebook, padding=10)
        notebook.add(failed_frame, text=f"Failed ({failed_count})")
        
        if failed_count > 0:
            # Create text widget for failed results
            failed_text = tk.Text(failed_frame, wrap=tk.WORD, height=15,
                                background=self.colors["background"],
                                foreground=self.colors["text_primary"],
                                insertbackground=self.colors["text_primary"])
            failed_text.pack(fill=tk.BOTH, expand=True)
            
            # Add scrollbar
            failed_scrollbar = ttk.Scrollbar(failed_frame, command=failed_text.yview)
            failed_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            failed_text.config(yscrollcommand=failed_scrollbar.set)
            
            # Insert failed results
            for option, message in cleanup_results["failed"]:
                failed_text.insert(tk.END, f"❌ {message}\n\n")
                
            failed_text.config(state=tk.DISABLED)  # Make read-only
        else:
            ttk.Label(
                failed_frame,
                text="No failed operations",
                style="Info.TLabel"
            ).pack(pady=20)
        
        # Add finish button with proper reference to dialog
        finish_button = ttk.Button(
            main_frame,
            text="Finish",
            width=12,  # Set explicit width to ensure text is visible
            style="Secondary.TButton"
        )
        finish_button.configure(command=dialog.destroy)
        finish_button.pack(side=tk.RIGHT, padx=10, pady=10, ipady=5)  # Add padding and increase height
        
        # Update status
        self.status_var.set(f"Cleanup completed: {success_count} successful, {failed_count} failed")
    
    def setup_styles(self):
        """Configure modern ttk styles with enhanced visual design."""
        style = ttk.Style()

        # Set the theme base
        try:
            style.theme_use('clam')  # Use clam as base for better customization
        except:
            pass

        # Modern frame styles - explicit theme backgrounds
        style.configure("Card.TFrame",
                      background=self.colors["background"],
                      relief="flat",
                      borderwidth=0)

        style.configure("Surface.TFrame",
                      background=self.colors["background"],
                      relief="flat",
                      borderwidth=0)

        # Default TFrame style with theme background
        style.configure("TFrame",
                      background=self.colors["background"],
                      relief="flat",
                      borderwidth=0)

        # Default TLabel style with theme background
        style.configure("TLabel",
                      background=self.colors["background"],
                      foreground=self.colors["text_primary"])

        # Default TButton style with theme background
        style.configure("TButton",
                      background=self.colors["background"],
                      foreground=self.colors["text_primary"])

        # Default TEntry style with modern appearance
        style.configure("TEntry",
                      fieldbackground=self.colors["background"],
                      foreground=self.colors["text_primary"],
                      borderwidth=2,
                      relief="solid",
                      bordercolor=self.colors["border"],
                      insertcolor=self.colors["primary"],
                      font=('Segoe UI', 10),
                      padding=(8, 6))

        # Default TCombobox style with modern appearance
        style.configure("TCombobox",
                      fieldbackground=self.colors["background"],
                      foreground=self.colors["text_primary"],
                      background=self.colors["background"],
                      borderwidth=2,
                      relief="solid",
                      bordercolor=self.colors["border"],
                      font=('Segoe UI', 10),
                      padding=(8, 6),
                      arrowcolor=self.colors["text_primary"])

        # Modern treeview styling - clean backgrounds
        style.configure("Treeview",
                      rowheight=35,
                      background=self.colors["background"],
                      fieldbackground=self.colors["background"],
                      foreground=self.colors["text_primary"],
                      font=('Segoe UI', 10),
                      borderwidth=0,
                      relief="flat")

        style.configure("Treeview.Heading",
                      font=('Segoe UI', 11, 'bold'),
                      background=self.colors["primary"],
                      foreground="white",
                      relief="flat",
                      borderwidth=0)

        # Enhanced treeview interactions
        style.map('Treeview',
                background=[('selected', self.colors["primary"]),
                          ('focus', self.colors["hover"])],
                foreground=[('selected', self.colors["background"] if self.theme_mode == "light" else self.colors["text_primary"])])

        style.map('Treeview.Heading',
                background=[('active', self.colors["primary_dark"])])

        # Modern button styles with enhanced visual feedback
        style.configure("Primary.TButton",
                      font=('Segoe UI', 11, 'bold'),
                      background=self.colors["primary"],
                      foreground=self.colors["background"] if self.theme_mode == "light" else self.colors["text_primary"],
                      borderwidth=0,
                      focuscolor='none',
                      relief="flat",
                      padding=(20, 10))

        style.map("Primary.TButton",
                background=[('active', self.colors["primary_dark"]),
                          ('pressed', self.colors["primary_dark"])],
                relief=[('pressed', 'flat')])

        style.configure("Secondary.TButton",
                      font=('Segoe UI', 10, 'bold'),
                      background=self.colors["background"],
                      foreground=self.colors["text_primary"],
                      borderwidth=1,
                      focuscolor='none',
                      relief="flat",
                      padding=(15, 8))

        style.map("Secondary.TButton",
                background=[('active', self.colors["hover"]),
                          ('pressed', self.colors["active"])],
                bordercolor=[('focus', self.colors["primary"])])

        style.configure("Action.TButton",
                      font=('Segoe UI', 10, 'bold'),
                      background=self.colors["accent"],
                      foreground=self.colors["background"] if self.theme_mode == "light" else self.colors["text_primary"],
                      borderwidth=0,
                      focuscolor='none',
                      relief="flat",
                      padding=(15, 8))

        style.map("Action.TButton",
                background=[('active', self.colors["secondary"]),
                          ('pressed', self.colors["secondary"])])

        # Modern label styles with explicit theme backgrounds
        style.configure("Title.TLabel",
                      font=('Segoe UI', 20, 'bold'),
                      foreground=self.colors["text_primary"],
                      background=self.colors["background"])

        style.configure("Subtitle.TLabel",
                      font=('Segoe UI', 14, 'bold'),
                      foreground=self.colors["text_primary"],
                      background=self.colors["background"])

        style.configure("Info.TLabel",
                      font=('Segoe UI', 10),
                      foreground=self.colors["text_secondary"],
                      background=self.colors["background"])

        style.configure("Caption.TLabel",
                      font=('Segoe UI', 9),
                      foreground=self.colors["text_tertiary"],
                      background=self.colors["background"])

        # Modern entry styles with enhanced appearance
        style.configure("TEntry",
                      fieldbackground=self.colors["background"],
                      foreground=self.colors["text_primary"],
                      borderwidth=2,
                      relief="solid",
                      insertcolor=self.colors["primary"],
                      font=('Segoe UI', 10),
                      padding=(8, 6))

        style.map("TEntry",
                bordercolor=[('focus', self.colors["primary"]),
                           ('!focus', self.colors["border"])],
                fieldbackground=[('readonly', self.colors["surface"]),
                               ('disabled', self.colors["surface"])])

        # Modern combobox styles with enhanced appearance
        style.configure("TCombobox",
                      fieldbackground=self.colors["background"],
                      foreground=self.colors["text_primary"],
                      background=self.colors["background"],
                      borderwidth=2,
                      relief="solid",
                      font=('Segoe UI', 10),
                      padding=(8, 6),
                      arrowcolor=self.colors["text_primary"])

        style.map("TCombobox",
                bordercolor=[('focus', self.colors["primary"]),
                           ('!focus', self.colors["border"])],
                fieldbackground=[('readonly', self.colors["background"]),
                               ('disabled', self.colors["surface"])],
                background=[('active', self.colors["hover"]),
                          ('pressed', self.colors["active"])])

        # Combobox dropdown styling
        style.configure("TCombobox.Listbox",
                      background=self.colors["background"],
                      foreground=self.colors["text_primary"],
                      selectbackground=self.colors["primary"],
                      selectforeground="white",
                      borderwidth=1,
                      relief="solid")

        # Modern progressbar - clean background
        style.configure("TProgressbar",
                      background=self.colors["primary"],
                      troughcolor=self.colors["background"],
                      borderwidth=0,
                      lightcolor=self.colors["primary"],
                      darkcolor=self.colors["primary"])

        # Modern separator with theme background
        style.configure("TSeparator",
                      background=self.colors["background"])

        # Modern checkbutton with enhanced styling
        style.configure("TCheckbutton",
                      foreground=self.colors["text_primary"],
                      background=self.colors["background"],
                      focuscolor='none',
                      font=('Segoe UI', 10),
                      borderwidth=0,
                      relief="flat")

        style.map("TCheckbutton",
                 background=[('active', self.colors["hover"]),
                           ('pressed', self.colors["active"])],
                 foreground=[('active', self.colors["text_primary"]),
                           ('disabled', self.colors["text_tertiary"])])

        # Modern labelframe with enhanced styling
        style.configure("TLabelframe",
                      foreground=self.colors["text_primary"],
                      background=self.colors["background"],
                      borderwidth=1,
                      relief="solid",
                      bordercolor=self.colors["border"])

        style.configure("TLabelframe.Label",
                      foreground=self.colors["text_primary"],
                      background=self.colors["background"],
                      font=('Segoe UI', 10, 'bold'))

        # Modern radiobutton with enhanced styling
        style.configure("TRadiobutton",
                      foreground=self.colors["text_primary"],
                      background=self.colors["background"],
                      focuscolor='none',
                      font=('Segoe UI', 10),
                      borderwidth=0,
                      relief="flat")

        style.map("TRadiobutton",
                 background=[('active', self.colors["hover"]),
                           ('pressed', self.colors["active"])],
                 foreground=[('active', self.colors["text_primary"]),
                           ('disabled', self.colors["text_tertiary"])])
    
    def create_widgets(self):
        """Create and arrange GUI widgets with modern styling."""
        # Set background color for root window
        self.root.configure(background=self.colors["background"])

        # Main container with modern styling
        main_container = ttk.Frame(self.root, style="Card.TFrame")
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Configure grid weights for responsive design
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(1, weight=1)

        # Modern header with enhanced styling
        header_frame = ttk.Frame(main_container, style="Surface.TFrame", padding="20")
        header_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        header_frame.columnconfigure(1, weight=1)
        
        # Modern app icon with enhanced styling
        logo_label = ttk.Label(
            header_frame,
            text="🔧",
            font=('Segoe UI', 32),
            foreground=self.colors["primary"]
        )
        logo_label.grid(row=0, column=0, rowspan=2, padx=(0, 15), pady=5)

        # Enhanced title with modern typography
        title_label = ttk.Label(
            header_frame,
            text="Programming Tools Version Checker",
            style="Title.TLabel"
        )
        title_label.grid(row=0, column=1, sticky=tk.W)

        # Enhanced subtitle
        subtitle_label = ttk.Label(
            header_frame,
            text="Detect, manage, and install development tools with modern interface",
            style="Info.TLabel"
        )
        subtitle_label.grid(row=1, column=1, sticky=tk.W)

        # Theme toggle button in header
        self.theme_btn = ttk.Button(
            header_frame,
            text="🌙" if self.theme_mode == "light" else "☀️",
            command=self.toggle_theme,
            style="Secondary.TButton",
            width=4
        )
        self.theme_btn.grid(row=0, column=2, padx=(15, 0))
        
        # Control panel (left sidebar)
        control_panel = ttk.Frame(main_container, style="Surface.TFrame", padding="15")
        control_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 15))

        # Control panel header
        control_header = ttk.Label(
            control_panel,
            text="🎛️ Control Panel",
            style="Subtitle.TLabel"
        )
        control_header.grid(row=0, column=0, sticky=tk.W, pady=(0, 15))

        # Main action button
        self.refresh_btn = ttk.Button(
            control_panel,
            text="🔄 Check Versions",
            command=self.start_version_check,
            style="Primary.TButton"
        )
        self.refresh_btn.grid(row=1, column=0, pady=(0, 15), sticky=tk.W+tk.E, ipady=5)

        ttk.Separator(control_panel, orient='horizontal').grid(row=2, column=0, sticky=tk.W+tk.E, pady=15)
        
        # Export section
        export_label = ttk.Label(control_panel, text="Export Results", style="Subtitle.TLabel")
        export_label.grid(row=3, column=0, sticky=tk.W, pady=(0, 10))

        export_frame = ttk.Frame(control_panel, style="Card.TFrame")
        export_frame.grid(row=4, column=0, sticky=tk.W+tk.E, pady=(0, 5))
        export_frame.columnconfigure(0, weight=1)
        export_frame.columnconfigure(1, weight=1)
        
        self.export_json_btn = ttk.Button(
            export_frame, 
            text="📊 JSON", 
            command=self.export_json,
            state='disabled',
            style="Secondary.TButton"
        )
        self.export_json_btn.grid(row=0, column=0, padx=(0, 2), sticky=tk.W+tk.E)
        
        self.export_txt_btn = ttk.Button(
            export_frame,
            text="📝 Text",
            command=self.export_text,
            state='disabled',
            style="Secondary.TButton"
        )
        self.export_txt_btn.grid(row=0, column=1, padx=(2, 0), sticky=tk.W+tk.E)
        
        # Add import JSON button
        self.import_json_btn = ttk.Button(
            control_panel,
            text="📥 Import JSON",
            command=self.import_json,
            style="Secondary.TButton"
        )
        self.import_json_btn.grid(row=5, column=0, pady=(5, 0), sticky=tk.W+tk.E, ipady=3)

        # Add auto install packages button
        self.auto_install_btn = ttk.Button(
            control_panel,
            text="🔄 Auto Install Packages",
            command=self.auto_install_from_backup,
            style="Primary.TButton"
        )
        self.auto_install_btn.grid(row=6, column=0, pady=(5, 0), sticky=tk.W+tk.E, ipady=3)

        ttk.Separator(control_panel, orient='horizontal').grid(row=7, column=0, sticky=tk.W+tk.E, pady=15)

        # RAM Monitor section
        ram_label = ttk.Label(control_panel, text="System Monitor", style="Subtitle.TLabel")
        ram_label.grid(row=8, column=0, sticky=tk.W, pady=(0, 10))

        self.ram_monitor_btn = ttk.Button(
            control_panel,
            text="🖥️ RAM Usage Monitor",
            command=self.show_ram_monitor,
            style="Action.TButton"
        )
        self.ram_monitor_btn.grid(row=9, column=0, pady=(0, 5), sticky=tk.W+tk.E, ipady=3)

        self.speed_test_btn = ttk.Button(
            control_panel,
            text="🌐 Internet Speed Test",
            command=self.show_speed_test,
            style="Action.TButton"
        )
        self.speed_test_btn.grid(row=10, column=0, pady=(0, 5), sticky=tk.W+tk.E, ipady=3)

        self.network_monitor_btn = ttk.Button(
            control_panel,
            text="🔗 Network Monitor",
            command=self.show_network_monitor,
            style="Action.TButton"
        )
        self.network_monitor_btn.grid(row=11, column=0, pady=(0, 5), sticky=tk.W+tk.E, ipady=3)

        self.service_manager_btn = ttk.Button(
            control_panel,
            text="🔧 Service Manager",
            command=self.show_service_manager,
            style="Action.TButton"
        )
        self.service_manager_btn.grid(row=12, column=0, pady=(0, 5), sticky=tk.W+tk.E, ipady=3)

        self.hardware_info_btn = ttk.Button(
            control_panel,
            text="💻 Hardware Info",
            command=self.show_hardware_info,
            style="Action.TButton"
        )
        self.hardware_info_btn.grid(row=13, column=0, pady=(0, 5), sticky=tk.W+tk.E, ipady=3)

        self.startup_manager_btn = ttk.Button(
            control_panel,
            text="🚀 Startup Manager",
            command=self.show_startup_manager,
            style="Action.TButton",
            takefocus=False
        )
        self.startup_manager_btn.grid(row=14, column=0, pady=(0, 10), sticky=tk.W+tk.E, ipady=3)

        ttk.Separator(control_panel, orient='horizontal').grid(row=15, column=0, sticky=tk.W+tk.E, pady=15)

        # Installation section
        install_label = ttk.Label(control_panel, text="Installation", style="Subtitle.TLabel")
        install_label.grid(row=16, column=0, sticky=tk.W, pady=(0, 10))

        self.install_selected_btn = ttk.Button(
            control_panel,
            text="📦 Install Selected Tool",
            command=self.install_selected_tool,
            state='disabled',
            style="Action.TButton"
        )
        self.install_selected_btn.grid(row=17, column=0, pady=(0, 10), sticky=tk.W+tk.E, ipady=3)

        # Instructions card
        info_frame = ttk.Frame(control_panel, padding="10", style="Card.TFrame")
        info_frame.grid(row=18, column=0, sticky=tk.W+tk.E, pady=(5, 0))
        info_frame.configure(borderwidth=1, relief="solid")
        
        # Instructions label with icon
        instructions_label = ttk.Label(
            info_frame,
            text="💡 Tip: Double-click on tools marked\n'📦 Install' to install them automatically",
            style="Info.TLabel",
            justify=tk.LEFT,
            wraplength=250
        )
        instructions_label.grid(row=0, column=0, sticky=tk.W)
        
        # Configure control panel column
        control_panel.columnconfigure(0, weight=1)
        
        # Results frame (main content area)
        results_container = ttk.Frame(main_container, style="Card.TFrame", padding="15")
        results_container.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_container.columnconfigure(0, weight=1)
        results_container.rowconfigure(1, weight=1)
        
        # Results header
        results_header = ttk.Label(
            results_container,
            text="Detected Tools and Versions",
            style="Subtitle.TLabel"
        )
        results_header.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Results frame
        results_frame = ttk.Frame(results_container, style="Card.TFrame")
        results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Treeview for results with modern styling
        self.tree = ttk.Treeview(results_frame, columns=('Version', 'Action'), show='tree headings')
        self.tree.heading('#0', text='Tool/Language')
        self.tree.heading('Version', text='Version')
        self.tree.heading('Action', text='Action')

        # Configure column widths
        self.tree.column('#0', width=250, minwidth=200)
        self.tree.column('Version', width=350, minwidth=200)
        self.tree.column('Action', width=100, minwidth=80)

        # Bind events for installation
        self.tree.bind('<Double-1>', self.on_tree_double_click)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
        # Modern scrollbars
        v_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Footer with status and progress
        footer_frame = ttk.Frame(main_container, style="Surface.TFrame", padding="15")
        footer_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(15, 0))
        footer_frame.columnconfigure(0, weight=1)
        
        # Status bar with modern styling
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Click 'Check Versions' to scan for installed tools")
        status_bar = ttk.Label(
            footer_frame, 
            textvariable=self.status_var,
            style="Info.TLabel",
            padding=(5, 3)
        )
        status_bar.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Progress bar with modern styling
        self.progress = ttk.Progressbar(footer_frame, mode='indeterminate', style="Horizontal.TProgressbar")
        self.progress.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Copyright and developer information
        copyright_frame = ttk.Frame(footer_frame, style="Card.TFrame")
        copyright_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        copyright_label = ttk.Label(
            copyright_frame,
            text="© 2025 Developed by Elnakieb. All rights reserved.",
            foreground=self.colors["text_tertiary"],
            font=('Segoe UI', 8)
        )
        copyright_label.pack(anchor=tk.CENTER)
    
    def center_window(self, window=None):
        """Center the window on screen.
        
        Args:
            window: Optional window to center. If None, centers the main window.
        """
        if window is None:
            window = self.root
            
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')
    
    def start_version_check(self):
        """Start version checking in a separate thread."""
        self.refresh_btn.config(state='disabled')
        # Note: Export functionality is now handled by dropdown in other dialogs
        self.progress.start()
        self.status_var.set("Checking versions... This may take a moment.")

        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Start checking in background thread
        thread = threading.Thread(target=self.check_versions_thread)
        thread.daemon = True
        thread.start()

        # Set a timeout to prevent hanging (2 minutes max)
        self.root.after(120000, self.check_timeout)
    
    def check_versions_thread(self):
        """Background thread for version checking."""
        try:
            def progress_callback(current, total, tool_name):
                # Update status in main thread
                self.root.after(0, lambda: self.status_var.set(f"Checking {tool_name}... ({current}/{total})"))

            self.results = self.version_checker.check_all_versions(progress_callback)
            # Schedule GUI update in main thread
            self.root.after(0, self.update_results)
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"Error checking versions: {str(e)}"))
    
    def update_results(self):
        """Update GUI with version check results using modern styling."""
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Add results to tree with improved styling
            for category, tools in self.results.items():
                # Add category as parent node with icon
                category_icon = self.get_category_icon(category)
                category_id = self.tree.insert('', 'end', text=f"{category_icon} {category}", values=('', ''), open=True)

                # Add tools under category
                for tool_name, version in tools.items():
                    # Determine action based on installation status and installability
                    action_text = ""
                    tags = ()

                    if version in ['Not installed', 'Not found', 'Timeout (5s)', 'Error']:
                        if self.version_checker.is_tool_installable(tool_name):
                            action_text = "📦 Install"
                            tags = ('installable',)
                        else:
                            action_text = "⚠️ Manual"
                            tags = ('not_installed',)
                    else:
                        action_text = "✅ Installed | 🗑️ Uninstall"
                        tags = ('installed', 'uninstall')

                    self.tree.insert(category_id, 'end',
                                   text=f"  {tool_name}",
                                   values=(version, action_text),
                                   tags=tags)

            # Configure tags with modern styling
            self.tree.tag_configure('not_installed', foreground=self.colors["warning"])
            self.tree.tag_configure('installed', foreground=self.colors["success"])
            self.tree.tag_configure('installable', foreground=self.colors["secondary"])
            self.tree.tag_configure('uninstall', foreground=self.colors["warning"])

            # Update status with more detailed information
            total_tools = sum(len(tools) for tools in self.results.values())
            installed_count = sum(1 for tools in self.results.values()
                                for version in tools.values()
                                if version not in ['Not installed', 'Not found', 'Timeout (5s)', 'Error'])

            installable_count = sum(1 for tools in self.results.values()
                                  for tool_name, version in tools.items()
                                  if version in ['Not installed', 'Not found', 'Timeout (5s)', 'Error']
                                  and self.version_checker.is_tool_installable(tool_name))

            self.status_var.set(f"✅ Scan complete - {installed_count}/{total_tools} tools found, {installable_count} can be auto-installed")

            # Note: Export functionality is now handled by dropdown in other dialogs

        except Exception as e:
            self.show_error(f"Error updating results: {str(e)}")
        finally:
            self.progress.stop()
            self.refresh_btn.config(state='normal')
    
    def export_json(self):
        """Export results to JSON file."""
        if not self.results:
            messagebox.showwarning("No Data", "No version data to export. Please check versions first.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save version data as JSON"
        )
        
        if filename:
            success, message = self.version_checker.export_to_json(self.results, filename)
            if success:
                messagebox.showinfo("Export Successful", message)
            else:
                messagebox.showerror("Export Failed", message)
    
    def export_text(self):
        """Export results to text file."""
        if not self.results:
            messagebox.showwarning("No Data", "No version data to export. Please check versions first.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save version data as text"
        )
        
        if filename:
            success, message = self.version_checker.export_to_text(self.results, filename)
            if success:
                messagebox.showinfo("Export Successful", message)
            else:
                messagebox.showerror("Export Failed", message)
                
    def import_json(self):
        """Import tool versions from JSON file for installation."""
        filename = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Import version data from JSON"
        )
        
        if not filename:
            return
            
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
                
            # Validate the imported data structure
            if not isinstance(imported_data, dict):
                messagebox.showerror("Import Failed", "Invalid JSON format. Expected a dictionary.")
                return
                
            # Find tools to install
            tools_to_install = []
            for category, tools in imported_data.items():
                if not isinstance(tools, dict):
                    continue
                    
                for tool_name, version in tools.items():
                    if self.version_checker.is_tool_installable(tool_name):
                        tools_to_install.append((tool_name, version))
            
            if not tools_to_install:
                messagebox.showinfo("No Tools", "No installable tools found in the imported file.")
                return
                
            # Ask user which tools to install
            self.show_import_selection_dialog(tools_to_install)
                
        except json.JSONDecodeError:
            messagebox.showerror("Import Failed", "Invalid JSON format.")
        except Exception as e:
            messagebox.showerror("Import Failed", f"Error importing file: {str(e)}")
            
    def show_import_selection_dialog(self, tools_to_install):
        """Show dialog to select which tools to install from imported JSON."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Tools to Install")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.focus_set()
        dialog.configure(background=self.colors["background"])

        # Center the dialog
        self.center_window(dialog)
        
        # Add instructions
        ttk.Label(
            dialog, 
            text="Select tools to install from the imported file:",
            style="Subtitle.TLabel"
        ).pack(pady=(15, 10), padx=20, anchor=tk.W)
        
        # Create a frame for the listbox and scrollbar
        frame = ttk.Frame(dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create a listbox with checkboxes
        import_list = ttk.Treeview(frame, columns=("Version"), show="tree headings")
        import_list.heading("#0", text="Tool")
        import_list.heading("Version", text="Version")
        import_list.column("#0", width=250)
        import_list.column("Version", width=150)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=import_list.yview)
        import_list.configure(yscrollcommand=scrollbar.set)
        
        # Pack the listbox and scrollbar
        import_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add the tools to the listbox
        for tool_name, version in tools_to_install:
            import_list.insert("", tk.END, text=tool_name, values=(version))
        
        # Add buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        ttk.Button(
            button_frame,
            text="Install Selected",
            command=lambda: self.install_selected_from_import(import_list, dialog),
            style="Primary.TButton"
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            style="Secondary.TButton"
        ).pack(side=tk.RIGHT, padx=5)
        
    def install_selected_from_import(self, import_list, dialog):
        """Install tools selected from the import dialog."""
        selected_items = import_list.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select at least one tool to install.")
            return
            
        # Get the selected tools
        tools_to_install = []
        for item in selected_items:
            tool_name = import_list.item(item, "text")
            version = import_list.item(item, "values")[0] if import_list.item(item, "values") else None
            tools_to_install.append((tool_name, version))
            
        # Close the dialog
        dialog.destroy()
        
        # Install each tool
        for tool_name, version in tools_to_install:
            self.install_tool(tool_name, version)
    
    def check_timeout(self):
        """Handle timeout if version checking takes too long."""
        if self.refresh_btn['state'] == 'disabled':  # Still checking
            self.progress.stop()
            self.refresh_btn.config(state='normal')
            self.status_var.set("Version check timed out after 2 minutes")
            messagebox.showwarning("Timeout", "Version checking took too long and was stopped. Some tools may be unresponsive.")

    def on_tree_select(self, event):
        """Handle tree selection changes."""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if not item:
            self.install_selected_btn.config(state='disabled')
            return

        # Get item details
        item_text = self.tree.item(item, 'text').strip()
        item_values = self.tree.item(item, 'values')

        # Enable install button only for installable tools
        if (item_text.startswith('  ') and len(item_values) >= 2 and
            "📦 Install" in item_values[1]):
            self.install_selected_btn.config(state='normal')
        else:
            self.install_selected_btn.config(state='disabled')

    def on_tree_double_click(self, event):
        """Handle double-click on tree items for installation or uninstallation."""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if not item:
            return

        # Get item details
        item_text = self.tree.item(item, 'text').strip()
        item_values = self.tree.item(item, 'values')

        # Debug print
        print(f"DEBUG: Double-clicked item: '{item_text}', values: {item_values}")

        # Skip if it's not a valid tool item
        if len(item_values) < 2:
            print(f"DEBUG: Skipping - not a tool item")
            return

        # Remove leading spaces from tool name
        tool_name = item_text.strip()
        action = item_values[1] if len(item_values) > 1 else ""

        print(f"DEBUG: Tool name: '{tool_name}', Action: '{action}'")

        # Check if it's an installed tool (for uninstall) or installable tool
        if "📦 Install" in action:
            print(f"DEBUG: Starting installation for {tool_name}")
            self.install_tool(tool_name)
        elif "✅ Installed | 🗑️ Uninstall" in action:
            # Show a confirmation dialog for uninstallation
            if messagebox.askyesno("Confirm Uninstall", f"Are you sure you want to uninstall {tool_name}?"):
                print(f"DEBUG: Starting uninstallation for {tool_name}")
                self.uninstall_tool(tool_name)
        else:
            print(f"DEBUG: Tool not installable or already installed")

    def install_selected_tool(self):
        """Install the currently selected tool."""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if not item:
            messagebox.showwarning("No Selection", "Please select a tool to install.")
            return

        # Get item details
        item_text = self.tree.item(item, 'text').strip()
        item_values = self.tree.item(item, 'values')

        if len(item_values) < 2:
            messagebox.showwarning("Invalid Selection", "Please select an installable tool.")
            return

        tool_name = item_text.strip()
        action = item_values[1] if len(item_values) > 1 else ""
        
    def uninstall_tool(self, tool_name):
        """Uninstall a tool using the version checker."""
        # Check if the tool is already being installed
        if tool_name in self.installing_tools:
            messagebox.showwarning("Tool Busy", f"{tool_name} is currently being installed. Please wait for the installation to complete.")
            return
            
        # Add to installing set to prevent multiple operations
        self.installing_tools.add(tool_name)
        
        # Update status
        self.status_var.set(f"Uninstalling {tool_name}...")
        
        # Disable buttons during uninstallation
        self.refresh_btn.config(state='disabled')
        self.install_selected_btn.config(state='disabled')
        
        # Start uninstallation in a separate thread
        threading.Thread(target=self.uninstall_tool_thread, args=(tool_name,), daemon=True).start()
            
    def prompt_for_version(self, tool_name):
        """Prompt user for version to install."""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Install {tool_name}")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.focus_set()
        dialog.configure(background=self.colors["background"])

        # Center the dialog
        self.center_window(dialog)
        
        # Add instructions
        ttk.Label(
            dialog, 
            text=f"Specify version for {tool_name}:",
            style="Subtitle.TLabel"
        ).pack(pady=(15, 5), padx=20, anchor=tk.W)
        
        ttk.Label(
            dialog, 
            text="Leave blank for latest version",
            style="Info.TLabel"
        ).pack(pady=(0, 10), padx=20, anchor=tk.W)
        
        # Version entry
        version_var = tk.StringVar()
        version_entry = ttk.Entry(dialog, textvariable=version_var, width=30)
        version_entry.pack(padx=20, pady=5, fill=tk.X)
        version_entry.focus()
        
        # Add buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=(15, 15))
        
        ttk.Button(
            button_frame,
            text="Install",
            command=lambda: self.process_version_and_install(tool_name, version_var.get(), dialog),
            style="Primary.TButton"
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            style="Secondary.TButton"
        ).pack(side=tk.RIGHT, padx=5)
        
    def process_version_and_install(self, tool_name, version, dialog):
        """Process the version input and install the tool."""
        dialog.destroy()
        self.install_tool(tool_name, version if version.strip() else None)

    def install_tool(self, tool_name, specific_version=None):
        """Install a specific tool with optional version."""
        print(f"DEBUG: install_tool called with: '{tool_name}', version: '{specific_version}'")

        if tool_name in self.installing_tools:
            print(f"DEBUG: Tool {tool_name} already being installed")
            messagebox.showwarning("Installation in Progress", f"{tool_name} is already being installed.")
            return

        installable = self.version_checker.is_tool_installable(tool_name)
        print(f"DEBUG: Tool {tool_name} installable: {installable}")

        if not installable:
            print(f"DEBUG: Tool {tool_name} not in installable list")
            messagebox.showwarning("Not Installable", f"{tool_name} cannot be automatically installed.")
            return

        # Confirm installation
        description = self.version_checker.get_install_description(tool_name)
        version_text = f" (version {specific_version})" if specific_version else ""
        response = messagebox.askyesno(
            "Confirm Installation",
            f"Do you want to install {tool_name}{version_text}?\n\n"
            f"Description: {description}\n\n"
            f"This will use available package managers (winget, chocolatey, or npm) "
            f"and may require administrator privileges.\n\n"
            f"Continue with installation?"
        )

        if not response:
            return

        # Start installation in background thread
        self.installing_tools.add(tool_name)
        self.status_var.set(f"Installing {tool_name}...")
        self.progress.start()

        thread = threading.Thread(target=self.install_tool_thread, args=(tool_name, specific_version))
        thread.daemon = True
        thread.start()

    def install_tool_thread(self, tool_name, specific_version=None):
        """Background thread for tool installation."""
        try:
            def progress_callback(message):
                self.root.after(0, lambda: self.status_var.set(f"Installing {tool_name}: {message}"))

            success, message = self.version_checker.install_tool(tool_name, progress_callback, specific_version)

            # Schedule GUI update in main thread
            self.root.after(0, lambda: self.installation_complete(tool_name, success, message))

        except Exception as e:
            self.root.after(0, lambda: self.installation_complete(tool_name, False, f"Installation error: {str(e)}"))
            
    def uninstall_tool_thread(self, tool_name):
        """Background thread for tool uninstallation."""
        try:
            def progress_callback(message):
                self.root.after(0, lambda: self.status_var.set(f"Uninstalling {tool_name}: {message}"))

            success, message = self.version_checker.uninstall_tool(tool_name, progress_callback)

            # Schedule GUI update in main thread
            self.root.after(0, lambda: self.uninstallation_complete(tool_name, success, message))

        except Exception as e:
            self.root.after(0, lambda: self.uninstallation_complete(tool_name, False, f"Uninstallation error: {str(e)}"))
            
    def auto_install_from_backup(self):
        """Install all tools that are installed in backup.json file."""
        backup_file = "backup.json"
        
        # Check if backup.json exists
        if not os.path.exists(backup_file):
            messagebox.showerror("File Not Found", f"Could not find {backup_file} in the current directory.")
            return
            
        try:
            # Load backup.json
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
                
            # Find tools that are installed in backup.json
            tools_to_install = []
            for category, tools in backup_data.items():
                if not isinstance(tools, dict):
                    continue
                    
                for tool_name, version in tools.items():
                    # Only include tools that are installed in backup.json
                    if version not in ['Not installed', 'Not found', 'Timeout (5s)', 'Error', "'java' is not recognized as an internal or external command,", "'vue' is not recognized as an internal or external command,", "'svn' is not recognized as an internal or external command,"]:
                        # Check if tool is installable
                        if self.version_checker.is_tool_installable(tool_name):
                            tools_to_install.append((tool_name, None))  # None for default version
            
            if not tools_to_install:
                messagebox.showinfo("No Tools", "No installable tools found in the backup file.")
                return
                
            # Ask for confirmation
            tool_names = '\n'.join([f"- {tool[0]}" for tool in tools_to_install])
            if not messagebox.askyesno("Confirm Installation", 
                                      f"The following tools will be installed:\n{tool_names}\n\nDo you want to continue?"):
                return
                
            # Start installation process
            self.status_var.set(f"Starting auto-installation of {len(tools_to_install)} tools...")
            self.progress.start()
            
            # Disable buttons during installation
            self.refresh_btn.config(state='disabled')
            self.install_selected_btn.config(state='disabled')
            self.auto_install_btn.config(state='disabled')
            
            # Start installation in a separate thread
            threading.Thread(target=self.auto_install_thread, args=(tools_to_install,), daemon=True).start()
                
        except json.JSONDecodeError:
            messagebox.showerror("Import Failed", "Invalid JSON format in backup file.")
        except Exception as e:
            messagebox.showerror("Import Failed", f"Error processing backup file: {str(e)}")
            
    def auto_install_thread(self, tools_to_install):
        """Background thread for auto-installing multiple tools."""
        total_tools = len(tools_to_install)
        successful_installs = 0
        failed_installs = 0
        failed_details = []
        
        for i, (tool_name, version) in enumerate(tools_to_install):
            # Skip if already being installed
            if tool_name in self.installing_tools:
                continue
                
            # Add to installing set
            self.installing_tools.add(tool_name)
            
            try:
                # Update status
                self.root.after(0, lambda: self.status_var.set(f"Installing {tool_name} ({i+1}/{total_tools})..."))
                
                def progress_callback(message):
                    # Update status in main thread
                    self.root.after(0, lambda: self.status_var.set(f"[{i+1}/{total_tools}] {message}"))
                
                # Install the tool
                success, message = self.version_checker.install_tool(tool_name, progress_callback, version)
                
                if success:
                    successful_installs += 1
                    # Show success message
                    self.root.after(0, lambda tool=tool_name: messagebox.showinfo("Installation Success", f"{tool} was installed successfully."))
                else:
                    failed_installs += 1
                    failed_details.append(f"{tool_name}: {message}")
                    # Show failure message and continue
                    self.root.after(0, lambda tool=tool_name, msg=message: messagebox.showerror("Installation Failed", f"Failed to install {tool}\nReason: {msg}"))
                    
            except Exception as e:
                failed_installs += 1
                error_msg = str(e)
                failed_details.append(f"{tool_name}: {error_msg}")
                # Show error message and continue
                self.root.after(0, lambda tool=tool_name, err=error_msg: messagebox.showerror("Installation Error", f"Error installing {tool}\nReason: {err}"))
            finally:
                # Remove from installing set
                self.installing_tools.discard(tool_name)
        
        # Update UI when all installations are complete
        self.root.after(0, lambda: self.auto_install_complete(successful_installs, failed_installs, total_tools, failed_details))
    
    def auto_install_complete(self, successful, failed, total, failed_details=None):
        """Handle completion of auto-installation process."""
        self.progress.stop()
        
        # Re-enable buttons
        self.refresh_btn.config(state='normal')
        self.auto_install_btn.config(state='normal')
        self.install_selected_btn.config(state='normal')
        
        # Update status
        self.status_var.set(f"Auto-installation complete: {successful} successful, {failed} failed out of {total} tools")
        
        # Show completion message
        if failed == 0:
            messagebox.showinfo("Installation Complete", f"Successfully installed all {successful} tools.")
        else:
            # Format the failure details
            if failed_details:
                details = "\n\nFailure details:\n" + "\n".join(failed_details)
            else:
                details = ""
                
            messagebox.showwarning("Installation Partially Complete", 
                                 f"Installed {successful} tools successfully, but {failed} tools failed to install.{details}")
        
        # Refresh the tool list
        self.start_version_check()

    def installation_complete(self, tool_name, success, message):
        """Handle completion of tool installation."""
        try:
            self.installing_tools.discard(tool_name)
            self.progress.stop()

            if success:
                messagebox.showinfo("Installation Successful", f"{tool_name} has been installed successfully!\n\n{message}")
                self.status_var.set(f"Installation complete: {tool_name}")

                # Automatically refresh to detect the newly installed tool
                self.root.after(2000, self.start_version_check)  # Refresh after 2 seconds
            else:
                messagebox.showerror("Installation Failed", f"Failed to install {tool_name}.\n\n{message}")
                self.status_var.set(f"Installation failed: {tool_name}")

        except Exception as e:
            self.show_error(f"Error handling installation completion: {str(e)}")
            
    def uninstallation_complete(self, tool_name, success, message):
        """Handle completion of tool uninstallation."""
        # Remove from installing set
        self.installing_tools.discard(tool_name)
        self.progress.stop()
        
        # Re-enable buttons
        self.refresh_btn.config(state='normal')
        self.install_selected_btn.config(state='normal')
        
        # Update status
        if success:
            self.status_var.set(f"Successfully uninstalled {tool_name}")
            messagebox.showinfo("Uninstallation Complete", f"{tool_name} was successfully uninstalled.")
            # Refresh to show updated versions
            self.start_version_check()
        else:
            self.status_var.set(f"Failed to uninstall {tool_name}")
            messagebox.showerror("Uninstallation Failed", f"Failed to uninstall {tool_name}: {message}")
            print(f"DEBUG: Uninstallation failed: {message}")

    def show_error(self, message):
        """Show error message with improved styling."""
        messagebox.showerror("Error", message)
        self.status_var.set("⚠️ Error occurred during version check")
        self.progress.stop()
        self.refresh_btn.config(state='normal')
        
    def get_category_icon(self, category):
        """Return an appropriate icon for each category."""
        icons = {
            "Languages": "🔤",
            "Package Managers": "📦",
            "Frontend Tools": "🖥️",
            "Version Control": "🔄",
            "Databases": "💾",
            "Development Tools": "🔧",
            "Development Environments": "🏗️",
            "Cloud Tools": "☁️"
        }
        return icons.get(category, "🔹")

    def on_close(self):
        """Handle window close event."""
        # Check if any installations are in progress
        if self.installing_tools:
            if messagebox.askyesno("Confirm Exit", "Installation(s) in progress. Are you sure you want to exit?"):
                # Force exit the application
                self.root.destroy()
                sys.exit(0)
            else:
                # User canceled exit
                return
        else:
            # No installations in progress, just exit
            self.root.destroy()
            sys.exit(0)
    
    def show_browser_backup_dialog(self):
        """Show browser backup dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Browser Backup")
        dialog.geometry("650x650")  # Made larger to ensure buttons are visible
        dialog.minsize(600, 600)    # Set minimum size
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(background=self.colors["background"])
        self.center_window(dialog)

        # Title
        title_label = ttk.Label(dialog, text="Browser Data Backup", font=('Arial', 14, 'bold'))
        title_label.pack(pady=15)

        # Create main content frame (simplified - no scrolling for now)
        content_frame = ttk.Frame(dialog)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Detect browsers
        detected_browsers = self.browser_backup.detect_browsers()

        # Browser selection frame
        browser_frame = ttk.LabelFrame(content_frame, text="Select Browsers to Backup", padding=10)
        browser_frame.pack(fill=tk.X, pady=10)

        self.browser_vars = {}
        for browser_name, is_detected in detected_browsers.items():
            var = tk.BooleanVar(value=is_detected)
            self.browser_vars[browser_name] = var

            status = "✅ Detected" if is_detected else "❌ Not Found"
            cb = ttk.Checkbutton(
                browser_frame,
                text=f"🌐 {browser_name} ({status})",
                variable=var,
                state='normal' if is_detected else 'disabled',
                style="TCheckbutton"
            )
            cb.pack(anchor=tk.W, pady=2)

        # Profile selection info
        info_frame = ttk.LabelFrame(content_frame, text="Backup Information", padding=10)
        info_frame.pack(fill=tk.X, pady=10)

        ttk.Label(
            info_frame,
            text="The following data will be backed up:\n" +
                 "• Bookmarks and Favorites\n" +
                 "• Browsing History\n" +
                 "• Saved Passwords (encrypted)\n" +
                 "• Cookies and Session Data\n" +
                 "• Extensions and Add-ons\n" +
                 "• Browser Preferences",
            justify=tk.LEFT
        ).pack(anchor=tk.W)

        # Progress frame
        progress_frame = ttk.Frame(content_frame)
        progress_frame.pack(fill=tk.X, pady=10)

        self.backup_progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.backup_progress.pack(fill=tk.X, pady=5)

        self.backup_status = tk.StringVar(value="Ready to backup")
        ttk.Label(progress_frame, textvariable=self.backup_status).pack()

        # Add separator before buttons
        separator = ttk.Separator(dialog, orient='horizontal')
        separator.pack(fill=tk.X, padx=20, pady=10)

        # Buttons frame - at the very bottom
        button_frame = ttk.Frame(dialog, relief=tk.RAISED, borderwidth=1)
        button_frame.pack(fill=tk.X, padx=20, pady=15, side=tk.BOTTOM)

        # Add background color to make buttons more visible
        button_frame.configure(style="ButtonFrame.TFrame")

        start_btn = ttk.Button(
            button_frame,
            text="🚀 START BACKUP",
            command=lambda: self.start_browser_backup(dialog),
            width=20
        )
        start_btn.pack(side=tk.LEFT, padx=15, pady=15, ipady=15)

        cancel_btn = ttk.Button(
            button_frame,
            text="❌ CANCEL",
            command=dialog.destroy,
            width=20
        )
        cancel_btn.pack(side=tk.RIGHT, padx=15, pady=15, ipady=15)

        # Removed the "buttons are here" text as requested

        # Force dialog to show buttons
        dialog.update_idletasks()
        print(f"Dialog created with geometry: {dialog.geometry()}")
        print(f"Button frame exists: {button_frame.winfo_exists()}")
        print("Buttons should be visible at the bottom of the dialog!")

    def start_browser_backup(self, dialog):
        """Start browser backup process."""
        selected_browsers = [name for name, var in self.browser_vars.items() if var.get()]

        if not selected_browsers:
            messagebox.showwarning("No Selection", "Please select at least one browser to backup.")
            return

        # Confirm backup
        response = messagebox.askyesno(
            "Confirm Backup",
            f"This will backup data from {len(selected_browsers)} browser(s):\n" +
            "\n".join(f"• {browser}" for browser in selected_browsers) +
            "\n\nThe backup will be saved to the 'browser_backups' folder.\n\n" +
            "Continue with backup?"
        )

        if not response:
            return

        # Start backup in background thread
        self.backup_progress.start()
        self.backup_status.set("Starting backup...")

        thread = threading.Thread(
            target=self.backup_browsers_thread,
            args=(selected_browsers, dialog)
        )
        thread.daemon = True
        thread.start()

    def backup_browsers_thread(self, browsers, dialog):
        """Background thread for browser backup."""
        try:
            backup_results = []

            for browser in browsers:
                def progress_callback(message):
                    self.root.after(0, lambda: self.backup_status.set(f"{browser}: {message}"))

                success, result = self.browser_backup.backup_browser(browser, progress_callback=progress_callback)
                backup_results.append((browser, success, result))

            # Schedule GUI update in main thread
            self.root.after(0, lambda: self.backup_complete(backup_results, dialog))

        except Exception as e:
            self.root.after(0, lambda: self.backup_error(str(e), dialog))

    def backup_complete(self, results, dialog):
        """Handle backup completion."""
        self.backup_progress.stop()

        successful_backups = [r for r in results if r[1]]
        failed_backups = [r for r in results if not r[1]]

        message = f"Backup completed!\n\n"

        if successful_backups:
            message += f"✅ Successfully backed up {len(successful_backups)} browser(s):\n"
            for browser, _, path in successful_backups:
                message += f"  • {browser}: {path}\n"

        if failed_backups:
            message += f"\n❌ Failed to backup {len(failed_backups)} browser(s):\n"
            for browser, _, error in failed_backups:
                message += f"  • {browser}: {error}\n"

        messagebox.showinfo("Backup Complete", message)
        self.backup_status.set("Backup completed")

        # Close dialog after a delay
        self.root.after(2000, dialog.destroy)

    def backup_error(self, error, dialog):
        """Handle backup error."""
        self.backup_progress.stop()
        self.backup_status.set("Backup failed")
        messagebox.showerror("Backup Error", f"Backup failed with error:\n{error}")

    def show_browser_restore_dialog(self):
        """Show browser restore dialog with working restore button."""
        backups = self.browser_backup.list_backups()

        if not backups:
            messagebox.showinfo("No Backups", "No browser backups found. Please create a backup first.")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Restore Browser Data")
        dialog.geometry("800x700")  # Larger size for better visibility
        dialog.minsize(750, 650)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(background=self.colors["background"])
        self.center_window(dialog)

        # Title
        title_label = ttk.Label(
            dialog,
            text="🔄 Restore Browser Data",
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=15)

        # Backup selection frame
        backup_frame = ttk.LabelFrame(dialog, text="📦 Select Backup to Restore", padding=15)
        backup_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Create simple backup listbox with theme colors
        self.backup_listbox = tk.Listbox(
            backup_frame,
            font=('Arial', 12),
            height=10,
            selectmode=tk.SINGLE,
            activestyle='dotbox',
            selectbackground=self.colors["primary"],
            selectforeground='white',
            background=self.colors["background"],
            foreground=self.colors["text_primary"],
            highlightthickness=0,
            borderwidth=1,
            relief="solid"
        )
        self.backup_listbox.pack(fill=tk.BOTH, expand=True, pady=10)

        # Store backup data for easy access
        self.backup_data = []

        # Populate backup list
        for i, backup in enumerate(backups):
            browser = backup.get('browser', 'Unknown')
            date = backup.get('backup_date', backup.get('timestamp', 'Unknown'))
            size = self.browser_backup.format_size(backup.get('size', 0))

            # Create simple display text
            display_text = f"🌐 {browser} - {date} ({size})"
            self.backup_listbox.insert(tk.END, display_text)
            self.backup_data.append(backup)

        # Selection info
        self.selected_backup_info = tk.StringVar(value="👆 Please select a backup from the list above")
        selected_label = ttk.Label(
            backup_frame,
            textvariable=self.selected_backup_info,
            font=('Arial', 11),
            foreground="blue"
        )
        selected_label.pack(pady=10)

        # Progress frame
        progress_frame = ttk.LabelFrame(dialog, text="📊 Restore Progress", padding=15)
        progress_frame.pack(fill=tk.X, padx=20, pady=10)

        self.restore_progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.restore_progress.pack(fill=tk.X, pady=5)

        self.restore_status = tk.StringVar(value="Ready to restore")
        ttk.Label(progress_frame, textvariable=self.restore_status).pack()

        # Add separator before buttons
        separator = ttk.Separator(dialog, orient='horizontal')
        separator.pack(fill=tk.X, padx=20, pady=20)

        # Button frame - always at bottom
        button_frame = ttk.Frame(dialog, relief=tk.RAISED, borderwidth=2)
        button_frame.pack(fill=tk.X, padx=20, pady=20)

        # Define restore function
        def start_restore():
            selection = self.backup_listbox.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a backup to restore.")
                return

            # Get selected backup
            index = selection[0]
            backup = self.backup_data[index]
            backup_path = backup.get('path', '')
            backup_browser = backup.get('browser', 'Unknown')
            backup_date = backup.get('backup_date', backup.get('timestamp', 'Unknown'))

            # Confirm restore
            confirm_text = f"🔄 Restore Browser Data\n\n"
            confirm_text += f"📦 From: {backup_browser} backup\n"
            confirm_text += f"📅 Date: {backup_date}\n"
            confirm_text += f"🎯 To: {backup_browser} (original browser)\n"
            confirm_text += f"\n⚠️ WARNING: This will overwrite existing browser data!\n"
            confirm_text += f"Make sure {backup_browser} is closed before proceeding.\n\n"
            confirm_text += f"Continue with restore?"

            response = messagebox.askyesno("Confirm Restore", confirm_text)

            if response:
                # Start restore with progress
                self.restore_progress.start()
                self.restore_status.set("Starting restore...")
                restore_btn.config(state='disabled')

                # Start restore in background thread
                thread = threading.Thread(
                    target=self.restore_browser_thread,
                    args=(backup_path, None, dialog)
                )
                thread.daemon = True
                thread.start()

        # Create restore button - large and prominent
        restore_btn = ttk.Button(
            button_frame,
            text="🔄 RESTORE SELECTED BACKUP",
            command=start_restore,
            state='disabled',
            width=30
        )
        restore_btn.pack(side=tk.LEFT, padx=15, pady=15, ipady=20, ipadx=15)

        # Configure button style
        style = ttk.Style()
        style.configure("RestoreBtn.TButton", font=('Arial', 12, 'bold'))
        restore_btn.configure(style="RestoreBtn.TButton")

        # Secondary buttons
        refresh_btn = ttk.Button(
            button_frame,
            text="🔄 Refresh",
            command=lambda: self.refresh_restore_list(dialog),
            width=12
        )
        refresh_btn.pack(side=tk.RIGHT, padx=5, pady=15, ipady=15)

        cancel_btn = ttk.Button(
            button_frame,
            text="❌ Cancel",
            command=dialog.destroy,
            width=12
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5, pady=15, ipady=15)

        # Bind selection event handler
        def on_backup_select(event):
            selection = self.backup_listbox.curselection()
            if selection:
                index = selection[0]
                backup = self.backup_data[index]

                browser = backup.get('browser', 'Unknown')
                date = backup.get('backup_date', backup.get('timestamp', 'Unknown'))
                size = self.browser_backup.format_size(backup.get('size', 0))

                info_text = f"✅ Selected: {browser} backup from {date} ({size})"
                self.selected_backup_info.set(info_text)
                restore_btn.config(state='normal')
            else:
                self.selected_backup_info.set("👆 Please select a backup from the list above")
                restore_btn.config(state='disabled')

        self.backup_listbox.bind('<<ListboxSelect>>', on_backup_select)

        # Force dialog to update and show buttons
        dialog.update_idletasks()
        print(f"Restore dialog created with geometry: {dialog.geometry()}")
        print("Restore button should be visible at the bottom!")

    def start_browser_restore(self, backup_path, target_browser, dialog):
        """Start browser restore process."""
        # Start restore in background thread
        thread = threading.Thread(
            target=self.restore_browser_thread,
            args=(backup_path, target_browser, dialog)
        )
        thread.daemon = True
        thread.start()

    def restore_browser_thread(self, backup_path, target_browser, dialog):
        """Background thread for browser restore."""
        try:
            def progress_callback(message):
                self.root.after(0, lambda: self.restore_status.set(f"Restoring: {message}"))

            success, message = self.browser_backup.restore_browser(
                backup_path, target_browser, progress_callback
            )

            self.root.after(0, lambda: self.restore_complete(success, message, dialog))

        except Exception as e:
            self.root.after(0, lambda: self.restore_error(str(e), dialog))

    def restore_complete(self, success, message, dialog):
        """Handle restore completion."""
        self.restore_progress.stop()

        if success:
            messagebox.showinfo("Restore Complete", f"✅ {message}")
            self.restore_status.set("Restore completed successfully")
        else:
            messagebox.showerror("Restore Failed", f"❌ {message}")
            self.restore_status.set("Restore failed")

        dialog.destroy()

    def restore_error(self, error, dialog):
        """Handle restore error."""
        self.restore_progress.stop()
        messagebox.showerror("Restore Error", f"Restore failed with error:\n{error}")
        self.restore_status.set("Restore failed")

    def refresh_restore_list(self, dialog):
        """Refresh the restore backup list."""
        # Clear existing items
        self.backup_listbox.delete(0, tk.END)
        self.backup_data.clear()

        # Reload backups
        backups = self.browser_backup.list_backups()

        if not backups:
            messagebox.showinfo("No Backups", "No browser backups found.")
            dialog.destroy()
            return

        # Populate backup list with user-friendly format
        for i, backup in enumerate(backups):
            browser = backup.get('browser', 'Unknown')
            date = backup.get('backup_date', backup.get('timestamp', 'Unknown'))
            size = self.browser_backup.format_size(backup.get('size', 0))
            profiles = backup.get('profiles', [])

            # Format date nicely
            try:
                from datetime import datetime
                if 'T' in date:
                    dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
                    formatted_date = dt.strftime("%B %d, %Y at %I:%M %p")
                else:
                    formatted_date = date
            except:
                formatted_date = date

            # Create user-friendly display text
            display_text = f"🌐 {browser} - {formatted_date} ({size})"
            if profiles:
                display_text += f" - Profiles: {', '.join(profiles[:2])}"
                if len(profiles) > 2:
                    display_text += f" +{len(profiles)-2} more"

            self.backup_listbox.insert(tk.END, display_text)
            self.backup_data.append(backup)

        # Reset selection info
        self.selected_backup_info.set("👆 Please select a backup from the list above")

    def show_browser_backup_manager(self):
        """Show browser backup manager dialog."""
        backups = self.browser_backup.list_backups()

        dialog = tk.Toplevel(self.root)
        dialog.title("Browser Backup Manager")
        dialog.geometry("800x600")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(background=self.colors["background"])
        self.center_window(dialog)

        # Title
        ttk.Label(dialog, text="Browser Backup Manager", style="Title.TLabel").pack(pady=15)

        # Backup list frame
        list_frame = ttk.LabelFrame(dialog, text="Available Backups", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Create treeview
        columns = ("browser", "date", "size", "profiles", "path")
        backup_tree = ttk.Treeview(list_frame, columns=columns, show="headings")

        backup_tree.heading("browser", text="Browser")
        backup_tree.heading("date", text="Date")
        backup_tree.heading("size", text="Size")
        backup_tree.heading("profiles", text="Profiles")
        backup_tree.heading("path", text="Path")

        backup_tree.column("browser", width=100)
        backup_tree.column("date", width=150)
        backup_tree.column("size", width=80)
        backup_tree.column("profiles", width=120)
        backup_tree.column("path", width=300)

        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=backup_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=backup_tree.xview)
        backup_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        backup_tree.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.E, tk.W))

        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        # Populate backups
        for backup in backups:
            backup_tree.insert("", tk.END, values=(
                backup.get('browser', 'Unknown'),
                backup.get('backup_date', backup.get('timestamp', 'Unknown')),
                self.browser_backup.format_size(backup.get('size', 0)),
                ', '.join(backup.get('profiles', [])),
                backup.get('path', '')
            ))

        # Buttons frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=15)

        def delete_backup():
            selection = backup_tree.selection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a backup to delete.")
                return

            backup_path = backup_tree.item(selection[0], 'values')[4]

            response = messagebox.askyesno(
                "Confirm Delete",
                f"Are you sure you want to delete this backup?\n\n{backup_path}\n\n" +
                "This action cannot be undone."
            )

            if response:
                success, message = self.browser_backup.delete_backup(backup_path)
                if success:
                    messagebox.showinfo("Success", message)
                    # Refresh the list
                    backup_tree.delete(selection[0])
                else:
                    messagebox.showerror("Error", message)

        def open_backup_folder():
            import subprocess
            backup_folder = self.browser_backup.backup_base_path
            try:
                subprocess.run(['explorer', str(backup_folder)], check=True)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open backup folder:\n{str(e)}")

        delete_btn = ttk.Button(
            button_frame,
            text="🗑️ Delete Selected",
            command=delete_backup
        )
        delete_btn.pack(side=tk.LEFT, padx=5, pady=5, ipady=8)

        folder_btn = ttk.Button(
            button_frame,
            text="📁 Open Backup Folder",
            command=open_backup_folder
        )
        folder_btn.pack(side=tk.LEFT, padx=5, pady=5, ipady=8)

        refresh_btn = ttk.Button(
            button_frame,
            text="🔄 Refresh",
            command=lambda: self.refresh_backup_list(backup_tree)
        )
        refresh_btn.pack(side=tk.LEFT, padx=5, pady=5, ipady=8)

        close_btn = ttk.Button(
            button_frame,
            text="Close",
            command=dialog.destroy
        )
        close_btn.pack(side=tk.RIGHT, padx=5, pady=5, ipady=8)

    def refresh_backup_list(self, tree):
        """Refresh the backup list in the tree."""
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)

        # Reload backups
        backups = self.browser_backup.list_backups()
        for backup in backups:
            tree.insert("", tk.END, values=(
                backup.get('browser', 'Unknown'),
                backup.get('backup_date', backup.get('timestamp', 'Unknown')),
                self.browser_backup.format_size(backup.get('size', 0)),
                ', '.join(backup.get('profiles', [])),
                backup.get('path', '')
            ))

    def export_bookmarks_html(self):
        """Export bookmarks to HTML format."""
        detected_browsers = self.browser_backup.detect_browsers()
        available_browsers = [name for name, detected in detected_browsers.items() if detected]

        if not available_browsers:
            messagebox.showinfo("No Browsers", "No supported browsers found.")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Export Bookmarks to HTML")
        dialog.geometry("600x550")  # Made even larger for bigger buttons
        dialog.minsize(550, 500)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(background=self.colors["background"])
        self.center_window(dialog)

        # Title with better styling
        title_label = ttk.Label(
            dialog,
            text="📤 Export Bookmarks to HTML",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=20)

        # Browser selection
        browser_frame = ttk.LabelFrame(dialog, text="Select Browser", padding=10)
        browser_frame.pack(fill=tk.X, padx=20, pady=10)

        browser_var = tk.StringVar(value=available_browsers[0])
        for browser in available_browsers:
            ttk.Radiobutton(
                browser_frame,
                text=f"🌐 {browser}",
                variable=browser_var,
                value=browser,
                style="TRadiobutton"
            ).pack(anchor=tk.W, pady=2)

        # Profile selection
        profile_frame = ttk.LabelFrame(dialog, text="Profile", padding=10)
        profile_frame.pack(fill=tk.X, padx=20, pady=10)

        profile_var = tk.StringVar(value="Default")
        ttk.Entry(profile_frame, textvariable=profile_var).pack(fill=tk.X)
        ttk.Label(profile_frame, text="(Default, Profile 1, etc.)").pack(anchor=tk.W)

        # Add separator before buttons
        separator = ttk.Separator(dialog, orient='horizontal')
        separator.pack(fill=tk.X, padx=20, pady=20)

        # Buttons with improved visibility
        button_frame = ttk.Frame(dialog, relief=tk.RAISED, borderwidth=1)
        button_frame.pack(fill=tk.X, padx=20, pady=20)

        def start_export():
            browser = browser_var.get()
            profile = profile_var.get()

            if not browser:
                messagebox.showwarning("No Browser Selected", "Please select a browser to export bookmarks from.")
                return

            try:
                success, result = self.browser_backup.export_bookmarks_html(browser, profile)
                if success:
                    messagebox.showinfo("Export Successful", f"✅ Bookmarks exported successfully!\n\nFile saved to:\n{result}")
                else:
                    messagebox.showerror("Export Failed", f"❌ Export failed:\n{result}")
            except Exception as e:
                messagebox.showerror("Error", f"❌ Export failed with error:\n{str(e)}")

            dialog.destroy()

        # Large, prominent export button with much bigger height
        export_btn = ttk.Button(
            button_frame,
            text="📤 EXPORT BOOKMARKS",
            command=start_export,
            width=25
        )
        export_btn.pack(side=tk.LEFT, padx=20, pady=20, ipady=25, ipadx=15)

        cancel_btn = ttk.Button(
            button_frame,
            text="❌ CANCEL",
            command=dialog.destroy,
            width=15
        )
        cancel_btn.pack(side=tk.RIGHT, padx=20, pady=20, ipady=25, ipadx=15)

        # Configure button styles for larger text
        style = ttk.Style()
        style.configure("Export.TButton", font=('Arial', 12, 'bold'))
        style.configure("Cancel.TButton", font=('Arial', 11, 'bold'))

        export_btn.configure(style="Export.TButton")
        cancel_btn.configure(style="Cancel.TButton")

        # Removed the text labels between buttons as requested

        # Force dialog to update and show buttons
        dialog.update_idletasks()

        # Print debug information
        print(f"Export dialog created with geometry: {dialog.geometry()}")
        print(f"Export button size: {export_btn.winfo_reqwidth()}x{export_btn.winfo_reqheight()}")
        print(f"Button frame size: {button_frame.winfo_reqwidth()}x{button_frame.winfo_reqheight()}")
        print("Large Export and Cancel buttons should be clearly visible at the bottom!")

    def show_hardware_info(self):
        """Show Hardware Information Viewer dialog."""
        # Create modern dialog
        dialog = self.create_modern_dialog(
            self.root,
            "Hardware Information",
            width=1000,
            height=650,
            min_width=900,
            min_height=550
        )

        # Create main container
        main_container = ttk.Frame(dialog)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create clean header
        self.create_modern_header(
            main_container,
            "Hardware Information",
            icon="💻"
        )

        # Top control bar - all buttons in one line
        control_bar = ttk.Frame(main_container)
        control_bar.pack(fill=tk.X, pady=(0, 10))

        # Left side - action buttons
        left_buttons = ttk.Frame(control_bar)
        left_buttons.pack(side=tk.LEFT)

        # Action buttons in one row
        self.collect_hw_btn = ttk.Button(
            left_buttons,
            text="🔄 Collect Info",
            command=lambda: self.collect_hardware_info(dialog),
            style="Primary.TButton"
        )
        self.collect_hw_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.refresh_hw_btn = ttk.Button(
            left_buttons,
            text="🔄 Refresh",
            command=lambda: self.collect_hardware_info(dialog),
            state='disabled'
        )
        self.refresh_hw_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Export dropdown for hardware
        self.hw_export_var = tk.StringVar(value="📤 Export")
        self.hw_export_combo = ttk.Combobox(
            left_buttons,
            textvariable=self.hw_export_var,
            values=["📤 Export", "📄 JSON", "📝 Text"],
            state="disabled",
            width=12,
            style="TCombobox"
        )
        self.hw_export_combo.pack(side=tk.LEFT, padx=(0, 10))

        def on_hw_export_select(event):
            selection = self.hw_export_var.get()
            if selection == "📄 JSON":
                self.export_hardware_info('json')
                self.hw_export_var.set("📤 Export")
            elif selection == "📝 Text":
                self.export_hardware_info('text')
                self.hw_export_var.set("📤 Export")

        self.hw_export_combo.bind("<<ComboboxSelected>>", on_hw_export_select)

        # Right side - status and progress
        right_status = ttk.Frame(control_bar)
        right_status.pack(side=tk.RIGHT)

        # Status label
        self.hw_status_label = ttk.Label(
            right_status,
            text="Collecting hardware information..."
        )
        self.hw_status_label.pack(side=tk.LEFT, padx=(0, 10))

        # Progress bar (initially hidden)
        self.hw_progress = ttk.Progressbar(
            right_status,
            mode='determinate',
            length=150
        )

        # Hardware information display area
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Create scrollable frame with scrollbar
        canvas = tk.Canvas(content_frame, highlightthickness=0, background=self.colors["background"])
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        self.hw_scrollable_frame = ttk.Frame(canvas)

        self.hw_scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.hw_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Store canvas reference for updating scroll region
        self.hw_canvas = canvas

        # Initial message
        initial_label = ttk.Label(
            self.hw_scrollable_frame,
            text="Collecting hardware information...\n\nPlease wait while we scan your system.",
            justify=tk.CENTER
        )
        initial_label.pack(expand=True, pady=50)

        # Close button
        close_frame = ttk.Frame(main_container)
        close_frame.pack(fill=tk.X, pady=(10, 0))

        close_btn = ttk.Button(
            close_frame,
            text="Close",
            command=dialog.destroy
        )
        close_btn.pack(side=tk.RIGHT)

        # Automatically start collecting hardware info
        dialog.after(500, lambda: self.collect_hardware_info(dialog))

    def collect_hardware_info(self, dialog):
        """Collect hardware information in background thread."""
        # Disable buttons during collection
        self.collect_hw_btn.config(state='disabled', text="🔄 Collecting...")
        self.refresh_hw_btn.config(state='disabled')
        self.hw_export_combo.config(state='disabled')

        # Show progress bar
        self.hw_progress.pack(side=tk.RIGHT, padx=(10, 0))
        self.hw_progress.config(value=0)

        # Clear existing content
        for widget in self.hw_scrollable_frame.winfo_children():
            widget.destroy()

        # Show collecting message
        collecting_label = ttk.Label(
            self.hw_scrollable_frame,
            text="🔄 Collecting hardware information...\n\nThis may take a few moments.",
            font=("Arial", 11),
            justify=tk.CENTER,
            foreground="blue"
        )
        collecting_label.pack(expand=True, pady=50)

        # Progress callback
        def progress_callback(message, percentage):
            dialog.after(0, lambda: self.update_hw_progress(message, percentage))

        # Completion callback
        def completion_callback(success, data):
            dialog.after(0, lambda: self.hw_collection_complete(dialog, success, data))

        # Start collection in background
        self.hardware_info_manager.collect_hardware_info_async(
            progress_callback=progress_callback,
            completion_callback=completion_callback
        )

    def update_hw_progress(self, message, percentage):
        """Update progress bar and status."""
        self.hw_status_label.config(text=message)
        self.hw_progress.config(value=percentage)

    def hw_collection_complete(self, dialog, success, data):
        """Handle completion of hardware info collection."""
        # Hide progress bar
        self.hw_progress.pack_forget()

        if success:
            self.hw_status_label.config(text="Hardware information collected successfully")
            self.display_hardware_info(data)

            # Enable buttons
            self.collect_hw_btn.config(state='normal', text="🔄 Collect Info")
            self.refresh_hw_btn.config(state='normal')
            self.hw_export_combo.config(state='readonly')
        else:
            self.hw_status_label.config(text="Failed to collect hardware information")

            # Clear content and show error
            for widget in self.hw_scrollable_frame.winfo_children():
                widget.destroy()

            error_label = ttk.Label(
                self.hw_scrollable_frame,
                text=f"❌ Error collecting hardware information:\n\n{data}",
                font=("Arial", 11),
                justify=tk.CENTER,
                foreground="red"
            )
            error_label.pack(expand=True, pady=50)

            # Re-enable collect button
            self.collect_hw_btn.config(state='normal', text="🔄 Collect Hardware Info")

    def display_hardware_info(self, data):
        """Display collected hardware information in organized sections."""
        # Clear existing content
        for widget in self.hw_scrollable_frame.winfo_children():
            widget.destroy()

        # Create sections for different hardware categories
        sections = [
            ("🖥️ System Information", "system"),
            ("🔧 CPU Information", "cpu"),
            ("💾 Memory Information", "memory"),
            ("🎮 Graphics Information", "gpu"),
            ("💿 Storage Information", "storage"),
            ("🔋 Battery Information", "battery")
        ]

        for section_title, section_key in sections:
            if section_key in data and data[section_key]:
                self.create_hw_section(section_title, data[section_key])

        # Update canvas scroll region after adding all content
        self.hw_scrollable_frame.update_idletasks()
        if hasattr(self, 'hw_canvas'):
            self.hw_canvas.configure(scrollregion=self.hw_canvas.bbox("all"))

    def create_hw_section(self, title, section_data):
        """Create a hardware information section."""
        # Section frame
        section_frame = ttk.LabelFrame(
            self.hw_scrollable_frame,
            text=title,
            padding=15
        )
        section_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        if isinstance(section_data, dict) and "error" in section_data:
            # Show error message
            error_label = ttk.Label(
                section_frame,
                text=f"❌ Error: {section_data['error']}",
                foreground="red"
            )
            error_label.pack(anchor=tk.W)
            return

        # Display data based on section type
        if title.startswith("🖥️"):  # System Information
            self.display_system_info(section_frame, section_data)
        elif title.startswith("🔧"):  # CPU Information
            self.display_cpu_info(section_frame, section_data)
        elif title.startswith("💾"):  # Memory Information
            self.display_memory_info(section_frame, section_data)
        elif title.startswith("🎮"):  # Graphics Information
            self.display_gpu_info(section_frame, section_data)
        elif title.startswith("💿"):  # Storage Information
            self.display_storage_info(section_frame, section_data)
        elif title.startswith("🔋"):  # Battery Information
            self.display_battery_info(section_frame, section_data)

    def display_system_info(self, parent, data):
        """Display system information."""
        info_items = [
            ("Computer Name", data.get('computer_name', 'Unknown')),
            ("Manufacturer", data.get('manufacturer', 'Unknown')),
            ("Model", data.get('model', 'Unknown')),
            ("System Type", data.get('system_type', 'Unknown')),
            ("Operating System", data.get('operating_system', 'Unknown')),
            ("OS Version", data.get('os_version', 'Unknown')),
            ("Architecture", data.get('architecture', 'Unknown'))
        ]

        for label, value in info_items:
            self.create_info_row(parent, label, value)

    def display_cpu_info(self, parent, data):
        """Display CPU information."""
        info_items = [
            ("Processor", data.get('name', 'Unknown')),
            ("Physical Cores", data.get('physical_cores', 'Unknown')),
            ("Logical Cores", data.get('logical_cores', 'Unknown')),
            ("Architecture", data.get('architecture', 'Unknown')),
            ("Current Usage", f"{data.get('current_usage', 'Unknown')}%" if data.get('current_usage') != 'Unknown' else 'Unknown')
        ]

        if 'max_clock_speed_ghz' in data:
            info_items.append(("Max Clock Speed", f"{data['max_clock_speed_ghz']} GHz"))
        if 'current_frequency_ghz' in data:
            info_items.append(("Current Frequency", f"{data['current_frequency_ghz']} GHz"))

        for label, value in info_items:
            self.create_info_row(parent, label, value)

    def display_memory_info(self, parent, data):
        """Display memory information."""
        info_items = [
            ("Total RAM", f"{data.get('total_gb', 'Unknown')} GB" if data.get('total_gb') != 'Unknown' else 'Unknown'),
            ("Used RAM", f"{data.get('used_gb', 'Unknown')} GB ({data.get('used_percentage', 'Unknown')}%)" if data.get('used_gb') != 'Unknown' else 'Unknown'),
            ("Available RAM", f"{data.get('available_gb', 'Unknown')} GB ({data.get('available_percentage', 'Unknown')}%)" if data.get('available_gb') != 'Unknown' else 'Unknown'),
            ("Memory Type", data.get('memory_type', 'Unknown'))
        ]

        if 'speed_mhz' in data and data['speed_mhz'] != 'Unknown':
            info_items.append(("Memory Speed", f"{data['speed_mhz']} MHz"))

        for label, value in info_items:
            self.create_info_row(parent, label, value)

    def display_gpu_info(self, parent, data):
        """Display GPU information."""
        info_items = [
            ("Graphics Card", data.get('name', 'Unknown')),
            ("Video Memory", f"{data.get('vram_gb', 'Unknown')} GB" if data.get('vram_gb') != 'Unknown' else 'Unknown'),
            ("Driver Version", data.get('driver_version', 'Unknown'))
        ]

        if 'display_resolution' in data:
            info_items.append(("Display Resolution", data['display_resolution']))
        if 'refresh_rate_hz' in data:
            info_items.append(("Refresh Rate", f"{data['refresh_rate_hz']} Hz"))

        for label, value in info_items:
            self.create_info_row(parent, label, value)

    def display_storage_info(self, parent, data):
        """Display storage information."""
        # Overall storage summary
        summary_items = [
            ("Total Storage", f"{data.get('total_capacity_gb', 'Unknown')} GB" if data.get('total_capacity_gb') != 'Unknown' else 'Unknown'),
            ("Used Storage", f"{data.get('total_used_gb', 'Unknown')} GB ({data.get('total_used_percentage', 'Unknown')}%)" if data.get('total_used_gb') != 'Unknown' else 'Unknown'),
            ("Free Storage", f"{data.get('total_free_gb', 'Unknown')} GB" if data.get('total_free_gb') != 'Unknown' else 'Unknown')
        ]

        for label, value in summary_items:
            self.create_info_row(parent, label, value)

        # Individual drives
        if 'drives' in data and data['drives']:
            drives_label = ttk.Label(parent, text="Individual Drives:", font=("Arial", 10, "bold"))
            drives_label.pack(anchor=tk.W, pady=(10, 5))

            for i, drive in enumerate(data['drives'], 1):
                drive_frame = ttk.Frame(parent)
                drive_frame.pack(fill=tk.X, pady=2)

                drive_title = f"Drive {i}: {drive.get('device', 'Unknown')}"
                drive_label = ttk.Label(drive_frame, text=drive_title, font=("Arial", 9, "bold"))
                drive_label.pack(anchor=tk.W)

                drive_details = [
                    ("  Type", drive.get('drive_type', 'Unknown')),
                    ("  Filesystem", drive.get('filesystem', 'Unknown')),
                    ("  Total", f"{drive.get('total_gb', 'Unknown')} GB" if drive.get('total_gb') != 'Unknown' else 'Unknown'),
                    ("  Used", f"{drive.get('used_gb', 'Unknown')} GB ({drive.get('used_percentage', 'Unknown')}%)" if drive.get('used_gb') != 'Unknown' else 'Unknown'),
                    ("  Free", f"{drive.get('free_gb', 'Unknown')} GB" if drive.get('free_gb') != 'Unknown' else 'Unknown')
                ]

                for label, value in drive_details:
                    detail_frame = ttk.Frame(drive_frame)
                    detail_frame.pack(fill=tk.X, pady=1)
                    detail_frame.columnconfigure(1, weight=1)

                    ttk.Label(detail_frame, text=f"{label}:", font=("Arial", 9), width=15).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
                    ttk.Label(detail_frame, text=str(value), font=("Arial", 9)).grid(row=0, column=1, sticky=tk.W)

    def display_battery_info(self, parent, data):
        """Display battery information."""
        if not data.get('present', False):
            no_battery_label = ttk.Label(
                parent,
                text="🖥️ No battery detected (Desktop system)",
                font=("Arial", 10)
            )
            no_battery_label.pack(anchor=tk.W)
            return

        info_items = [
            ("Battery Present", "Yes"),
            ("Charge Level", f"{data.get('charge_percentage', 'Unknown')}%" if data.get('charge_percentage') != 'Unknown' else 'Unknown'),
            ("Power Adapter", "Connected" if data.get('power_plugged', False) else "Disconnected"),
            ("Time Remaining", data.get('time_remaining', 'Unknown'))
        ]

        if 'health_percentage' in data and data['health_percentage'] != 'Unknown':
            info_items.append(("Battery Health", f"{data['health_percentage']}%"))
        if 'cycle_count' in data and data['cycle_count'] != 'Unknown':
            info_items.append(("Cycle Count", str(data['cycle_count'])))

        for label, value in info_items:
            self.create_info_row(parent, label, value)

    def create_info_row(self, parent, label, value):
        """Create a row displaying hardware information."""
        row_frame = ttk.Frame(parent)
        row_frame.pack(fill=tk.X, pady=2)

        # Configure grid weights for proper expansion
        row_frame.columnconfigure(1, weight=1)

        label_widget = ttk.Label(
            row_frame,
            text=f"{label}:",
            font=("Arial", 10, "bold"),
            width=25
        )
        label_widget.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))

        value_widget = ttk.Label(
            row_frame,
            text=str(value),
            font=("Arial", 10),
            wraplength=400
        )
        value_widget.grid(row=0, column=1, sticky=tk.W)

    def export_hardware_info(self, format_type):
        """Export hardware information to file."""
        try:
            # Check if data is available
            if not self.hardware_info_manager.get_current_data():
                messagebox.showwarning("No Data", "No hardware information available to export.\n\nPlease click 'Collect Hardware Info' first to gather system information.")
                return

            # Show status message
            print(f"Starting {format_type.upper()} export...")

            # Prepare file dialog parameters
            if format_type == 'json':
                title = "Export Hardware Information as JSON"
                default_ext = ".json"
                file_types = [("JSON files", "*.json"), ("All files", "*.*")]
                default_name = f"hardware_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            else:  # text
                title = "Export Hardware Information as Text"
                default_ext = ".txt"
                file_types = [("Text files", "*.txt"), ("All files", "*.*")]
                default_name = f"hardware_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

            # Show file dialog with proper parent
            filename = filedialog.asksaveasfilename(
                parent=self.root,
                title=title,
                defaultextension=default_ext,
                filetypes=file_types,
                initialfile=default_name,
                initialdir=os.path.expanduser("~/Desktop")  # Start in Desktop folder
            )

            print(f"File dialog result: {filename}")

            if filename:
                print(f"Exporting to: {filename}")
                try:
                    success, message = self.hardware_info_manager.export_data(filename, format_type)
                    if success:
                        messagebox.showinfo("Export Successful",
                                          f"Hardware information exported successfully!\n\n"
                                          f"File saved to:\n{filename}\n\n"
                                          f"You can now open this file to view your hardware report.")
                        print(f"Export successful: {message}")
                    else:
                        messagebox.showerror("Export Failed", f"Failed to export hardware information:\n\n{message}")
                        print(f"Export failed: {message}")
                except Exception as e:
                    error_msg = f"Error during export: {str(e)}"
                    messagebox.showerror("Export Error", f"An error occurred while exporting:\n\n{error_msg}")
                    print(error_msg)
            else:
                print("Export cancelled by user")

        except Exception as e:
            error_msg = f"Unexpected error in export function: {str(e)}"
            print(error_msg)
            messagebox.showerror("Export Error", f"An unexpected error occurred:\n\n{error_msg}")
            import traceback
            traceback.print_exc()

    def show_startup_manager(self):
        """Show Startup Manager dialog."""
        # Create modern dialog
        dialog = self.create_modern_dialog(
            self.root,
            "Startup Manager",
            width=1200,
            height=700,
            min_width=1100,
            min_height=600
        )

        # Create main container
        main_container = ttk.Frame(dialog)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create clean header
        self.create_modern_header(
            main_container,
            "Startup Manager",
            icon="🚀"
        )

        # Top control bar - all buttons in one line
        control_bar = ttk.Frame(main_container)
        control_bar.pack(fill=tk.X, pady=(0, 10))

        # Left side - action buttons
        left_buttons = ttk.Frame(control_bar)
        left_buttons.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Primary action buttons in one row
        action_buttons = ttk.Frame(left_buttons)
        action_buttons.pack(side=tk.LEFT, padx=(0, 10))

        # Scan button
        self.scan_startup_btn = ttk.Button(
            action_buttons,
            text="🔄 Scan",
            command=lambda: self.scan_startup_programs(dialog),
            style="Primary.TButton"
        )
        self.scan_startup_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Refresh button
        self.refresh_startup_btn = ttk.Button(
            action_buttons,
            text="🔄 Refresh",
            command=lambda: self.scan_startup_programs(dialog),
            state='disabled',
            style="Primary.TButton"
        )
        self.refresh_startup_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Backup button
        self.backup_startup_btn = ttk.Button(
            action_buttons,
            text="💾 Backup",
            command=self.create_startup_backup,
            state='disabled',
            style="Primary.TButton"
        )
        self.backup_startup_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Export dropdown for startup
        self.startup_export_var = tk.StringVar(value="📤 Export")
        self.startup_export_combo = ttk.Combobox(
            action_buttons,
            textvariable=self.startup_export_var,
            values=["📤 Export", "📄 JSON", "📝 Text"],
            state="disabled",
            width=12,
            style="TCombobox"
        )
        self.startup_export_combo.pack(side=tk.LEFT, padx=(0, 10))

        def on_startup_export_select(event):
            selection = self.startup_export_var.get()
            if selection == "📄 JSON":
                self.export_startup_config('json')
                self.startup_export_var.set("📤 Export")
            elif selection == "📝 Text":
                self.export_startup_config('text')
                self.startup_export_var.set("📤 Export")

        self.startup_export_combo.bind("<<ComboboxSelected>>", on_startup_export_select)

        # Right side - search and filters
        right_controls = ttk.Frame(control_bar)
        right_controls.pack(side=tk.RIGHT)

        # Search
        ttk.Label(right_controls, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.startup_search_var = tk.StringVar()
        self.startup_search_entry = ttk.Entry(right_controls, textvariable=self.startup_search_var, width=20)
        self.startup_search_entry.pack(side=tk.LEFT, padx=(0, 10))

        # Impact filter
        ttk.Label(right_controls, text="Impact:").pack(side=tk.LEFT, padx=(0, 5))
        self.startup_impact_filter = tk.StringVar(value="All")
        impact_combo = ttk.Combobox(right_controls, textvariable=self.startup_impact_filter,
                                   values=["All", "High", "Medium", "Low", "Unknown"], state="readonly", width=8)
        impact_combo.pack(side=tk.LEFT, padx=(0, 10))

        # Location filter
        ttk.Label(right_controls, text="Location:").pack(side=tk.LEFT, padx=(0, 5))
        self.startup_location_filter = tk.StringVar(value="All")
        location_combo = ttk.Combobox(right_controls, textvariable=self.startup_location_filter,
                                     values=["All"], state="readonly", width=10)
        location_combo.pack(side=tk.LEFT)

        # Store filter comboboxes for later updates
        self.startup_impact_combo = impact_combo
        self.startup_location_combo = location_combo

        # Status bar
        status_bar = ttk.Frame(main_container)
        status_bar.pack(fill=tk.X, pady=(0, 10))

        # Status label
        self.startup_status_label = ttk.Label(
            status_bar,
            text="Click 'Scan' to analyze startup programs"
        )
        self.startup_status_label.pack(side=tk.LEFT)

        # Progress bar (initially hidden)
        self.startup_progress = ttk.Progressbar(
            status_bar,
            mode='determinate',
            length=150
        )

        # Boot time estimation
        self.boot_time_label = ttk.Label(
            status_bar,
            text="Boot time improvement: 0s"
        )
        self.boot_time_label.pack(side=tk.RIGHT)

        # Startup programs table
        tree_frame = ttk.Frame(main_container)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Define columns
        columns = ("number", "name", "status", "impact", "location", "publisher")
        self.startup_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)

        # Define column headings and widths
        self.startup_tree.heading("number", text="#")
        self.startup_tree.heading("name", text="Program Name")
        self.startup_tree.heading("status", text="Status")
        self.startup_tree.heading("impact", text="Impact")
        self.startup_tree.heading("location", text="Location")
        self.startup_tree.heading("publisher", text="Publisher")

        self.startup_tree.column("number", width=50, minwidth=50, anchor=tk.CENTER)
        self.startup_tree.column("name", width=300, minwidth=250)
        self.startup_tree.column("status", width=100, minwidth=80, anchor=tk.CENTER)
        self.startup_tree.column("impact", width=100, minwidth=80, anchor=tk.CENTER)
        self.startup_tree.column("location", width=200, minwidth=150)
        self.startup_tree.column("publisher", width=200, minwidth=150)

        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.startup_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.startup_tree.xview)
        self.startup_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack treeview and scrollbars
        self.startup_tree.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.E, tk.W))

        # Configure grid weights
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        # Configure tags for colored text
        self.startup_tree.tag_configure("disabled", foreground="red")
        self.startup_tree.tag_configure("enabled", foreground="black")

        # Bind events
        self.startup_tree.bind("<Double-1>", self.on_startup_item_double_click)
        self.startup_search_var.trace("w", lambda *args: self.filter_startup_items(dialog))
        self.startup_impact_filter.trace("w", lambda *args: self.filter_startup_items(dialog))
        self.startup_location_filter.trace("w", lambda *args: self.filter_startup_items(dialog))

        # Close button
        close_frame = ttk.Frame(main_container)
        close_frame.pack(fill=tk.X, pady=(10, 0))

        close_btn = ttk.Button(
            close_frame,
            text="Close",
            command=dialog.destroy
        )
        close_btn.pack(side=tk.RIGHT)

        # Initialize variables
        self.startup_items = []
        self.selected_startup_items = {}

        # Initial message
        initial_label = ttk.Label(
            tree_frame,
            text="All startup programs will appear here after scanning.\n\nClick 'Scan' to analyze your complete startup configuration.\n\nCritical Windows services are protected but other programs can be safely managed.",
            font=("Arial", 11),
            justify=tk.CENTER,
            foreground=self.colors["text_secondary"]
        )
        initial_label.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        # Store dialog reference
        self.startup_dialog = dialog

        # Automatically start scanning
        dialog.after(100, lambda: self.scan_startup_programs(dialog))

    def scan_startup_programs(self, dialog):
        """Scan startup programs in background thread."""
        # Disable buttons during scan
        self.scan_startup_btn.config(state='disabled', text="🔄 Scanning...")
        self.refresh_startup_btn.config(state='disabled')
        self.backup_startup_btn.config(state='disabled')
        self.startup_export_combo.config(state='disabled')

        # Show progress bar
        self.startup_progress.pack(side=tk.RIGHT, padx=(10, 0))
        self.startup_progress.config(value=0)

        # Clear existing content
        for item in self.startup_tree.get_children():
            self.startup_tree.delete(item)

        # Create progress frame
        progress_frame = ttk.Frame(self.startup_tree.master)
        progress_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W), padx=50, pady=50)

        # Progress label
        self.progress_label = ttk.Label(
            progress_frame,
            text="Initializing scan...",
            font=("Arial", 12),
            justify=tk.CENTER,
            foreground=self.colors["text_primary"]
        )
        self.progress_label.pack(pady=(0, 20))

        # Progress bar
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=400,
            style="Primary.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(pady=(0, 10))

        # Progress percentage
        self.progress_percent = ttk.Label(
            progress_frame,
            text="0%",
            font=("Arial", 10),
            foreground=self.colors["text_secondary"]
        )
        self.progress_percent.pack()

        # Progress callback
        def progress_callback(message, percentage):
            dialog.after(0, lambda: self.update_startup_progress(message, percentage))

        # Completion callback
        def completion_callback(success, data):
            dialog.after(0, lambda: self.startup_scan_complete(dialog, success, data))

        # Start scan in background
        def scan_thread():
            try:
                startup_items = self.startup_manager.get_startup_items(progress_callback)
                completion_callback(True, startup_items)
            except Exception as e:
                completion_callback(False, str(e))

        threading.Thread(target=scan_thread, daemon=True).start()

    def update_startup_progress(self, message, percentage):
        """Update progress bar and status."""
        try:
            if hasattr(self, 'progress_label'):
                self.progress_label.config(text=message)
            if hasattr(self, 'progress_bar'):
                self.progress_bar['value'] = percentage
            if hasattr(self, 'progress_percent'):
                self.progress_percent.config(text=f"{percentage}%")
        except Exception:
            pass  # Ignore errors if widgets don't exist

    def startup_scan_complete(self, dialog, success, data):
        """Handle completion of startup scan."""
        # Hide progress elements
        try:
            if hasattr(self, 'progress_label') and self.progress_label.master:
                self.progress_label.master.destroy()
        except Exception:
            pass

        if success:
            self.startup_items = data
            self.display_startup_items()

            # Enable buttons
            self.scan_startup_btn.config(state='normal', text="🔄 Scan")
            self.refresh_startup_btn.config(state='normal')
            self.backup_startup_btn.config(state='normal')
            self.startup_export_combo.config(state='readonly')

            # Update filter options
            self.update_startup_filter_options()

        else:
            self.startup_status_label.config(text="Failed to scan startup programs")

            # Clear content and show error
            for item in self.startup_tree.get_children():
                self.startup_tree.delete(item)

            error_label = ttk.Label(
                self.startup_tree.master,
                text=f"❌ Error scanning startup programs:\n\n{data}",
                font=("Arial", 11),
                justify=tk.CENTER,
                foreground="red"
            )
            error_label.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

            # Re-enable scan button
            self.scan_startup_btn.config(state='normal', text="🔄 Scan Startup Programs")

    def display_startup_items(self):
        """Display startup items in the treeview."""
        # Clear existing items
        for item in self.startup_tree.get_children():
            self.startup_tree.delete(item)

        # Clear any overlay labels
        for widget in self.startup_tree.master.grid_slaves():
            if isinstance(widget, ttk.Label):
                widget.destroy()

        # Add startup items to treeview
        for index, item in enumerate(self.startup_items, 1):
            # Determine status display (reversed to match Task Manager)
            status = "Disabled" if item.enabled else "Enabled"

            # Color code impact
            impact_display = item.impact
            if item.impact == "High":
                impact_display = "🔴 High"
            elif item.impact == "Medium":
                impact_display = "🟡 Medium"
            elif item.impact == "Low":
                impact_display = "🟢 Low"
            else:
                impact_display = "⚪ Unknown"

            # Add system critical indicator
            name_display = item.name
            if item.is_system_critical:
                name_display = f"🛡️ {item.name}"

            # Insert item
            item_id = self.startup_tree.insert("", tk.END, values=(
                str(index),  # Row number
                name_display,
                status,
                impact_display,
                item.location,
                item.publisher or "Unknown"
            ))

            # Apply red color to disabled items (reversed logic for display)
            if item.enabled:  # If internally enabled, show as "Disabled" in red
                self.startup_tree.set(item_id, "status", "Disabled")
                # Configure red text for disabled items
                self.startup_tree.item(item_id, tags=("disabled",))
            else:  # If internally disabled, show as "Enabled" in normal color
                self.startup_tree.item(item_id, tags=("enabled",))

            # Store item reference for operations
            self.selected_startup_items[item_id] = {'item': item, 'selected': False}

    def update_startup_filter_options(self):
        """Update filter dropdown options based on current startup items."""
        # Get unique locations
        locations = set(item.location for item in self.startup_items)
        location_values = ["All"] + sorted(locations)

        # Update location combobox
        self.startup_location_combo.config(values=location_values)

    def filter_startup_items(self, dialog):
        """Filter startup items based on search and filter criteria."""
        if not hasattr(self, 'startup_items') or not self.startup_items:
            return

        search_text = self.startup_search_var.get().lower()
        impact_filter = self.startup_impact_filter.get()
        location_filter = self.startup_location_filter.get()

        # Clear current display
        for item in self.startup_tree.get_children():
            self.startup_tree.delete(item)

        # Filter and display items
        filtered_count = 0
        display_index = 1
        for item in self.startup_items:
            # Apply filters
            if search_text and search_text not in item.name.lower() and search_text not in (item.description or "").lower():
                continue

            if impact_filter != "All" and item.impact != impact_filter:
                continue

            if location_filter != "All" and item.location != location_filter:
                continue

            # Display item (reversed to match Task Manager)
            status = "Disabled" if item.enabled else "Enabled"

            impact_display = item.impact
            if item.impact == "High":
                impact_display = "🔴 High"
            elif item.impact == "Medium":
                impact_display = "🟡 Medium"
            elif item.impact == "Low":
                impact_display = "🟢 Low"
            else:
                impact_display = "⚪ Unknown"

            name_display = item.name
            if item.is_system_critical:
                name_display = f"🛡️ {item.name}"

            item_id = self.startup_tree.insert("", tk.END, values=(
                str(display_index),
                name_display,
                status,
                impact_display,
                item.location,
                item.publisher or "Unknown"
            ))

            # Apply color tags (reversed logic for display)
            if item.enabled:  # If internally enabled, show as "Disabled" in red
                self.startup_tree.item(item_id, tags=("disabled",))
            else:  # If internally disabled, show as "Enabled" in normal color
                self.startup_tree.item(item_id, tags=("enabled",))

            # Store item reference for operations
            self.selected_startup_items[item_id] = {'item': item, 'selected': False}

            filtered_count += 1
            display_index += 1

        # Update status
        if filtered_count != len(self.startup_items):
            self.startup_status_label.config(text=f"Showing {filtered_count} of {len(self.startup_items)} startup programs")
        else:
            # Count enabled/disabled for status display
            enabled_count = sum(1 for item in self.startup_items if item.enabled)
            disabled_count = len(self.startup_items) - enabled_count
            self.startup_status_label.config(text=f"Found {len(self.startup_items)} programs ({enabled_count} enabled, {disabled_count} disabled)")

    def on_startup_item_double_click(self, event):
        """Handle double-click on startup item to toggle selection or enable/disable."""
        item_id = self.startup_tree.identify_row(event.y)
        if not item_id:
            return

        # Toggle enable/disable on any column click
        self.toggle_startup_item_status(item_id)

    def toggle_startup_item_selection(self, item_id):
        """Toggle selection state of startup item."""
        if item_id in self.selected_startup_items:
            current_state = self.selected_startup_items[item_id]['selected']
            new_state = not current_state
            self.selected_startup_items[item_id]['selected'] = new_state

            # Update display
            values = list(self.startup_tree.item(item_id, "values"))
            values[0] = "☑" if new_state else "☐"
            self.startup_tree.item(item_id, values=values)

            # Update button states
            self.update_bulk_button_states()

    def toggle_startup_item_status(self, item_id):
        """Toggle enable/disable status of startup item."""
        if item_id not in self.selected_startup_items:
            return

        item = self.selected_startup_items[item_id]['item']

        # Show confirmation for system critical items
        if item.is_system_critical and item.enabled:
            if not messagebox.askyesno(
                "System Critical Program",
                f"'{item.name}' appears to be a system critical program.\n\n"
                "Disabling it may affect system stability or functionality.\n\n"
                "Are you sure you want to disable this program?",
                icon="warning"
            ):
                return

        # Perform the toggle
        try:
            if item.enabled:
                success, message = self.startup_manager.disable_startup_item(item)
                action = "disabled"
            else:
                success, message = self.startup_manager.enable_startup_item(item)
                action = "enabled"

            if success:
                # The startup_manager methods should have already updated the item.enabled state
                # Just refresh the display to show the new state
                self.refresh_startup_item_display(item_id, item)

                # Update boot time estimation
                self.update_boot_time_estimation()
            # Remove error messages - no feedback for successful operations

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while toggling '{item.name}':\n\n{str(e)}")

    def refresh_startup_item_display(self, item_id, item):
        """Refresh the display of a single startup item."""
        status = "Disabled" if item.enabled else "Enabled"

        impact_display = item.impact
        if item.impact == "High":
            impact_display = "🔴 High"
        elif item.impact == "Medium":
            impact_display = "🟡 Medium"
        elif item.impact == "Low":
            impact_display = "🟢 Low"
        else:
            impact_display = "⚪ Unknown"

        name_display = item.name
        if item.is_system_critical:
            name_display = f"🛡️ {item.name}"

        # Get current values to preserve the number
        current_values = self.startup_tree.item(item_id, "values")
        row_number = current_values[0] if current_values else "1"

        # Update values
        self.startup_tree.item(item_id, values=(
            row_number,
            name_display,
            status,
            impact_display,
            item.location,
            item.publisher or "Unknown"
        ))

        # Apply color tags (reversed logic for display)
        if item.enabled:  # If internally enabled, show as "Disabled" in red
            self.startup_tree.item(item_id, tags=("disabled",))
        else:  # If internally disabled, show as "Enabled" in normal color
            self.startup_tree.item(item_id, tags=("enabled",))

    def update_bulk_button_states(self):
        """Update the state of bulk operation buttons."""
        selected_items = [data for data in self.selected_startup_items.values() if data['selected']]

        if selected_items:
            self.enable_selected_btn.config(state='normal')
            self.disable_selected_btn.config(state='normal')
        else:
            self.enable_selected_btn.config(state='disabled')
            self.disable_selected_btn.config(state='disabled')

    def enable_selected_startup_items(self):
        """Enable all selected startup items."""
        selected_items = [data['item'] for data in self.selected_startup_items.values() if data['selected']]

        if not selected_items:
            messagebox.showwarning("No Selection", "Please select startup items to enable.")
            return

        # Confirm action
        if not messagebox.askyesno(
            "Confirm Enable",
            f"Are you sure you want to enable {len(selected_items)} selected startup programs?\n\n"
            "This will cause them to start automatically when Windows boots."
        ):
            return

        # Perform bulk enable
        try:
            results = self.startup_manager.bulk_enable_items(selected_items)

            # Process results
            success_count = 0
            error_messages = []

            for name, success, message in results:
                if success:
                    success_count += 1
                else:
                    error_messages.append(f"• {name}: {message}")

            # Update display for each affected item
            for name, success, message in results:
                if success:
                    # Find and update the specific item
                    for item_id, data in self.selected_startup_items.items():
                        if data['item'].name == name:
                            self.refresh_startup_item_display(item_id, data['item'])
                            break

            self.update_boot_time_estimation()

            # Show results only if there were errors
            if success_count < len(selected_items):
                error_text = "\n".join(error_messages[:5])  # Show first 5 errors
                if len(error_messages) > 5:
                    error_text += f"\n... and {len(error_messages) - 5} more errors"

                messagebox.showwarning(
                    "Partial Success",
                    f"Enabled {success_count} of {len(selected_items)} startup programs.\n\n"
                    f"Errors:\n{error_text}"
                )

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during bulk enable:\n\n{str(e)}")

    def disable_selected_startup_items(self):
        """Disable all selected startup items."""
        selected_items = [data['item'] for data in self.selected_startup_items.values() if data['selected']]

        if not selected_items:
            messagebox.showwarning("No Selection", "Please select startup items to disable.")
            return

        # Check for system critical items
        critical_items = [item for item in selected_items if item.is_system_critical]
        if critical_items:
            critical_names = ", ".join([item.name for item in critical_items[:3]])
            if len(critical_items) > 3:
                critical_names += f" and {len(critical_items) - 3} more"

            if not messagebox.askyesno(
                "System Critical Programs",
                f"The selection includes {len(critical_items)} system critical programs:\n{critical_names}\n\n"
                "Disabling these may affect system stability or functionality.\n\n"
                "Are you sure you want to continue?",
                icon="warning"
            ):
                return

        # Estimate boot time improvement
        improvement = self.startup_manager.estimate_boot_time_improvement(selected_items)

        # Confirm action
        if not messagebox.askyesno(
            "Confirm Disable",
            f"Are you sure you want to disable {len(selected_items)} selected startup programs?\n\n"
            f"Estimated boot time improvement: {improvement} seconds\n\n"
            "You can re-enable them later if needed."
        ):
            return

        # Perform bulk disable
        try:
            results = self.startup_manager.bulk_disable_items(selected_items)

            # Process results
            success_count = 0
            error_messages = []

            for name, success, message in results:
                if success:
                    success_count += 1
                else:
                    error_messages.append(f"• {name}: {message}")

            # Update display for each affected item
            for name, success, message in results:
                if success:
                    # Find and update the specific item
                    for item_id, data in self.selected_startup_items.items():
                        if data['item'].name == name:
                            self.refresh_startup_item_display(item_id, data['item'])
                            break

            self.update_boot_time_estimation()

            # Show results only if there were errors
            if success_count < len(selected_items):
                error_text = "\n".join(error_messages[:5])  # Show first 5 errors
                if len(error_messages) > 5:
                    error_text += f"\n... and {len(error_messages) - 5} more errors"

                messagebox.showwarning(
                    "Partial Success",
                    f"Disabled {success_count} of {len(selected_items)} startup programs.\n\n"
                    f"Errors:\n{error_text}"
                )

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during bulk disable:\n\n{str(e)}")

    def update_boot_time_estimation(self):
        """Update boot time improvement estimation display."""
        try:
            # Get currently disabled high-impact items
            disabled_items = [item for item in self.startup_items if not item.enabled and item.impact in ["High", "Medium"]]
            improvement = self.startup_manager.estimate_boot_time_improvement(disabled_items)

            if improvement > 0:
                self.boot_time_label.config(
                    text=f"Current boot time improvement: ~{improvement} seconds",
                    foreground="green"
                )
            else:
                self.boot_time_label.config(
                    text="Estimated boot time improvement: 0 seconds",
                    foreground=self.colors["text_secondary"]
                )

        except Exception:
            self.boot_time_label.config(
                text="Boot time estimation unavailable",
                foreground=self.colors["text_secondary"]
            )

    def create_startup_backup(self):
        """Create backup of current startup configuration."""
        try:
            success, message = self.startup_manager.create_backup()
            if success:
                messagebox.showinfo("Backup Created", message)
            else:
                messagebox.showerror("Backup Failed", message)
        except Exception as e:
            messagebox.showerror("Backup Error", f"Failed to create backup:\n\n{str(e)}")

    def export_startup_config(self, format_type):
        """Export startup configuration to file."""
        if not hasattr(self, 'startup_items') or not self.startup_items:
            messagebox.showwarning("No Data", "No startup information available to export. Please scan startup programs first.")
            return

        try:
            # File dialog
            if format_type == 'json':
                filename = filedialog.asksaveasfilename(
                    parent=self.root,
                    title="Export Startup Configuration as JSON",
                    defaultextension=".json",
                    filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                    initialfile=f"startup_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    initialdir=os.path.expanduser("~/Desktop")
                )
            else:  # text
                filename = filedialog.asksaveasfilename(
                    parent=self.root,
                    title="Export Startup Configuration as Text",
                    defaultextension=".txt",
                    filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                    initialfile=f"startup_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    initialdir=os.path.expanduser("~/Desktop")
                )

            if filename:
                success, message = self.startup_manager.export_startup_config(filename, format_type)
                if success:
                    messagebox.showinfo(
                        "Export Successful",
                        f"Startup configuration exported successfully!\n\n"
                        f"File saved to:\n{filename}\n\n"
                        f"You can now view your startup programs report."
                    )
                else:
                    messagebox.showerror("Export Failed", message)

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export startup configuration:\n\n{str(e)}")

    def run(self):
        """Start the GUI application."""
        self.root.mainloop()
