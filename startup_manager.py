#!/usr/bin/env python3
"""
Startup Manager Module - Clean Implementation
Provides comprehensive Windows startup program management with visual status indicators.
"""

import subprocess
import json
import platform
import threading
import time
import os
import re
import winreg
from datetime import datetime
from pathlib import Path
import psutil


class StartupItem:
    """Represents a single startup program item."""

    def __init__(self, name, path, location, enabled=True, publisher="", description="", impact="Medium"):
        self.name = name
        self.path = path
        self.location = location  # Registry, Folder, Service, Task
        self.enabled = enabled
        self.publisher = publisher
        self.description = description
        self.impact = impact  # High, Medium, Low
        self.startup_delay = 0
        self.last_modified = ""
        self.is_system_critical = False
        self.registry_key = ""
        self.registry_value = ""

    def to_dict(self):
        """Convert startup item to dictionary for export."""
        return {
            "name": self.name,
            "path": self.path,
            "location": self.location,
            "enabled": self.enabled,
            "publisher": self.publisher,
            "description": self.description,
            "impact": self.impact,
            "startup_delay": self.startup_delay,
            "last_modified": self.last_modified,
            "is_system_critical": self.is_system_critical
        }


class StartupScanner:
    """Scans system for startup programs from various locations."""

    def __init__(self):
        self.is_windows = platform.system().lower() == 'windows'
        self.startup_items = []

    def scan_all_startup_locations(self, progress_callback=None):
        """Scan all startup locations and return list of startup items."""
        try:
            self.startup_items = []

            if progress_callback:
                progress_callback("Scanning registry startup entries...", 20)
            self._scan_registry_startup()

            if progress_callback:
                progress_callback("Scanning startup folders...", 40)
            self._scan_startup_folders()

            if progress_callback:
                progress_callback("Scanning Windows services...", 60)
            self._scan_startup_services()

            if progress_callback:
                progress_callback("Scanning scheduled tasks...", 80)
            self._scan_scheduled_tasks()

            if progress_callback:
                progress_callback("Analyzing startup impact...", 90)
            self._analyze_startup_impact()

            if progress_callback:
                progress_callback("Scan complete", 100)

            return self.startup_items

        except Exception as e:
            print(f"Error scanning startup locations: {e}")
            return []
    
    def _scan_registry_startup(self):
        """Scan Windows Registry for startup entries."""
        if not self.is_windows:
            return

        # Registry locations to scan
        registry_locations = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", "Registry (User)"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", "Registry (System)"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce", "Registry (User Once)"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\RunOnce", "Registry (System Once)"),
        ]

        for hkey, subkey, location_name in registry_locations:
            try:
                # Scan enabled entries
                self._scan_registry_key(hkey, subkey, location_name, enabled=True)

                # Scan disabled entries (with _DISABLED suffix)
                self._scan_registry_key(hkey, subkey, location_name, enabled=False)

            except Exception as e:
                print(f"Error scanning registry {location_name}: {e}")
                continue

    def _scan_registry_key(self, hkey, subkey, location_name, enabled=True):
        """Scan a specific registry key for enabled or disabled entries."""
        try:
            with winreg.OpenKey(hkey, subkey) as key:
                i = 0
                while True:
                    try:
                        name, value, reg_type = winreg.EnumValue(key, i)

                        # Check if this is a disabled entry
                        if enabled and name.endswith("_DISABLED"):
                            i += 1
                            continue  # Skip disabled entries when looking for enabled
                        elif not enabled and not name.endswith("_DISABLED"):
                            i += 1
                            continue  # Skip enabled entries when looking for disabled

                        # Clean up name for disabled entries
                        display_name = name.replace("_DISABLED", "") if name.endswith("_DISABLED") else name

                        # Parse the command line to extract executable path
                        exe_path = self._extract_executable_path(value)

                        # Get file information
                        publisher, description = self._get_file_info(exe_path)

                        # Create startup item
                        startup_item = StartupItem(
                            name=display_name,
                            path=exe_path,
                            location=location_name,
                            enabled=enabled,
                            publisher=publisher,
                            description=description
                        )

                        startup_item.registry_key = subkey
                        startup_item.registry_value = display_name
                        startup_item.is_system_critical = self._is_critical_windows_component(display_name, exe_path)

                        # Only add if it's manageable
                        if self._is_manageable_item(startup_item):
                            self.startup_items.append(startup_item)
                        i += 1

                    except OSError:
                        break  # No more values

        except Exception as e:
            print(f"Error scanning registry key {subkey}: {e}")
    
    def _scan_startup_folders(self):
        """Scan Windows startup folders."""
        if not self.is_windows:
            return

        startup_folders = [
            (os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"), "Startup Folder (User)"),
            (os.path.expandvars(r"%ALLUSERSPROFILE%\Microsoft\Windows\Start Menu\Programs\Startup"), "Startup Folder (System)")
        ]

        for folder_path, location_name in startup_folders:
            try:
                if os.path.exists(folder_path):
                    # Scan enabled files
                    for item in os.listdir(folder_path):
                        if item.endswith('.disabled'):
                            continue  # Skip disabled files for now

                        item_path = os.path.join(folder_path, item)
                        if os.path.isfile(item_path):
                            self._create_folder_startup_item(item_path, location_name, enabled=True)

                    # Scan disabled files
                    for item in os.listdir(folder_path):
                        if not item.endswith('.disabled'):
                            continue  # Only process disabled files

                        item_path = os.path.join(folder_path, item)
                        if os.path.isfile(item_path):
                            # Remove .disabled extension for display
                            original_name = item[:-9]  # Remove .disabled
                            self._create_folder_startup_item(item_path, location_name, enabled=False, display_name=original_name)

            except Exception as e:
                print(f"Error scanning startup folder {folder_path}: {e}")
                continue

    def _create_folder_startup_item(self, item_path, location_name, enabled=True, display_name=None):
        """Create a startup item from a folder file."""
        try:
            item_name = os.path.basename(item_path)
            program_name = display_name or os.path.splitext(item_name)[0]

            # Get file information
            publisher, description = self._get_file_info(item_path)

            # Create startup item
            startup_item = StartupItem(
                name=program_name,
                path=item_path,
                location=location_name,
                enabled=enabled,
                publisher=publisher,
                description=description
            )

            startup_item.last_modified = self._get_file_modified_date(item_path)
            startup_item.is_system_critical = self._is_critical_windows_component(program_name, item_path)

            # Only add if it's manageable
            if self._is_manageable_item(startup_item):
                self.startup_items.append(startup_item)

        except Exception as e:
            print(f"Error creating folder startup item: {e}")

    def _is_critical_windows_component(self, name, path):
        """Determine if this is a critical Windows component that should be marked as such."""
        name_lower = name.lower()
        path_lower = path.lower() if path else ""

        # Critical Windows components (show but warn before disabling)
        critical_components = [
            'explorer', 'dwm', 'winlogon', 'ctfmon', 'sihost', 'runtimebroker',
            'searchui', 'startmenuexperiencehost', 'shellexperiencehost',
            'windows security', 'windows defender', 'audiodg', 'conhost',
            'taskhostw', 'backgroundtaskhost', 'applicationframehost'
        ]

        # Check against critical component names
        for component in critical_components:
            if component in name_lower:
                return True

        # Check if it's in Windows system directories
        if any(sys_dir in path_lower for sys_dir in ['system32', 'syswow64', 'windows\\system']):
            return True

        # Check for Windows executable patterns
        if any(pattern in path_lower for pattern in ['\\windows\\', 'c:\\windows']):
            return True

        return False
    
    def _scan_startup_services(self):
        """Scan Windows services set to automatic startup."""
        if not self.is_windows:
            return

        try:
            # Use WMI to get services with automatic start type
            result = subprocess.run([
                "powershell",
                "-ExecutionPolicy", "Bypass",
                "-Command",
                "Get-WmiObject -Class Win32_Service | Where-Object {$_.StartMode -eq 'Auto'} | ConvertTo-Json -Depth 2"
            ], capture_output=True, text=True, timeout=30, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

            if result.returncode == 0 and result.stdout.strip():
                try:
                    services_data = json.loads(result.stdout)
                    if not isinstance(services_data, list):
                        services_data = [services_data]

                    for service in services_data:
                        name = service.get('Name', 'Unknown')
                        display_name = service.get('DisplayName', name)
                        path_name = service.get('PathName', '')
                        description = service.get('Description', '')

                        # Extract executable path from service path
                        exe_path = self._extract_executable_path(path_name)

                        # Only exclude truly critical services
                        if not self._is_critical_service(name, display_name):
                            # Check actual service status
                            is_enabled = self._check_service_status(name)

                            startup_item = StartupItem(
                                name=display_name,
                                path=exe_path,
                                location="Windows Service",
                                enabled=is_enabled,
                                publisher="Microsoft Corporation",
                                description=description
                            )

                            # Mark as critical if it's a Windows system service
                            startup_item.is_system_critical = self._is_windows_system_service(display_name, description)

                            # Only add if it's manageable
                            if self._is_manageable_item(startup_item):
                                self.startup_items.append(startup_item)

                except json.JSONDecodeError:
                    print("Error parsing services JSON data")

        except Exception as e:
            print(f"Error scanning startup services: {e}")

    def _is_critical_service(self, name, display_name):
        """Check if this is a truly critical service that should be excluded."""
        critical_services = [
            'winlogon', 'csrss', 'smss', 'wininit', 'lsass', 'services',
            'rpcss', 'dcomlaunch', 'rpcendpointmapper', 'cryptsvc', 'eventlog',
            'dhcp', 'dnscache', 'netlogon', 'netman', 'nsi', 'plugplay',
            'power', 'schedule', 'spooler', 'themes', 'winmgmt', 'bits'
        ]

        name_lower = name.lower()
        display_lower = display_name.lower()

        for critical in critical_services:
            if critical in name_lower or critical in display_lower:
                return True

        return False

    def _is_windows_system_service(self, display_name, description):
        """Check if this is a Windows system service (for display marking)."""
        system_indicators = [
            'windows', 'microsoft', 'system', 'audio', 'network',
            'security', 'update', 'defender', 'firewall'
        ]

        text_to_check = f"{display_name} {description}".lower()

        for indicator in system_indicators:
            if indicator in text_to_check:
                return True

        return False

    def _check_service_status(self, service_name):
        """Check if a service is set to automatic startup."""
        try:
            result = subprocess.run([
                'sc', 'qc', service_name
            ], capture_output=True, text=True, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

            if result.returncode == 0:
                output = result.stdout.lower()
                return 'auto_start' in output or 'automatic' in output

            return True  # Default to enabled if we can't determine
        except Exception:
            return True
    
    def _scan_scheduled_tasks(self):
        """Scan Windows Task Scheduler for startup tasks."""
        if not self.is_windows:
            return

        try:
            # Get scheduled tasks that run at startup
            result = subprocess.run([
                "powershell",
                "-ExecutionPolicy", "Bypass",
                "-Command",
                "Get-ScheduledTask | Where-Object {$_.Triggers.TriggerType -contains 'AtStartup' -or $_.Triggers.TriggerType -contains 'AtLogOn'} | ConvertTo-Json -Depth 3"
            ], capture_output=True, text=True, timeout=30, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

            if result.returncode == 0 and result.stdout.strip():
                try:
                    tasks_data = json.loads(result.stdout)
                    if not isinstance(tasks_data, list):
                        tasks_data = [tasks_data]

                    for task in tasks_data:
                        task_name = task.get('TaskName', 'Unknown')
                        description = task.get('Description', '')
                        task_state = task.get('State', 'Unknown')

                        # Try to get the action (executable)
                        actions = task.get('Actions', [])
                        exe_path = ""
                        if actions and len(actions) > 0:
                            exe_path = actions[0].get('Execute', '')

                        # Include all tasks except truly critical ones
                        if not self._is_critical_service(task_name, task_name):
                            # Check if this task is actually enabled
                            is_enabled = self._check_task_status(task_name, task_state)

                            startup_item = StartupItem(
                                name=task_name,
                                path=exe_path,
                                location="Scheduled Task",
                                enabled=is_enabled,
                                publisher="Microsoft Corporation",
                                description=description
                            )

                            # Mark Windows tasks as critical for display purposes
                            startup_item.is_system_critical = self._is_critical_windows_component(task_name, exe_path)

                            # Only add if it's manageable
                            if self._is_manageable_item(startup_item):
                                self.startup_items.append(startup_item)

                except json.JSONDecodeError:
                    print("Error parsing scheduled tasks JSON data")

        except Exception as e:
            print(f"Error scanning scheduled tasks: {e}")

    def _check_task_status(self, task_name, task_state):
        """Check if a scheduled task is enabled."""
        try:
            # First check the state from the query
            if task_state.lower() == 'ready':
                return True
            elif task_state.lower() == 'disabled':
                return False

            # If unclear, query the task directly
            result = subprocess.run([
                'schtasks', '/query', '/tn', task_name, '/fo', 'csv'
            ], capture_output=True, text=True, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

            if result.returncode == 0:
                output = result.stdout.lower()
                if 'ready' in output:
                    return True
                elif 'disabled' in output:
                    return False

            return True  # Default to enabled if we can't determine
        except Exception:
            return True
    
    def _extract_executable_path(self, command_line):
        """Extract executable path from command line string."""
        if not command_line:
            return ""
        
        # Remove quotes and extract the executable path
        command_line = command_line.strip()
        
        # Handle quoted paths
        if command_line.startswith('"'):
            end_quote = command_line.find('"', 1)
            if end_quote != -1:
                return command_line[1:end_quote]
        
        # Handle unquoted paths (take first part before space)
        parts = command_line.split(' ')
        return parts[0] if parts else command_line
    
    def _get_file_info(self, file_path):
        """Get publisher and description information from file."""
        try:
            if not file_path or not os.path.exists(file_path):
                return "", ""
            
            # Use PowerShell to get file version info
            result = subprocess.run([
                "powershell",
                "-ExecutionPolicy", "Bypass",
                "-Command",
                f"(Get-ItemProperty '{file_path}').VersionInfo | ConvertTo-Json"
            ], capture_output=True, text=True, timeout=10, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result.returncode == 0 and result.stdout.strip():
                try:
                    version_info = json.loads(result.stdout)
                    publisher = version_info.get('CompanyName', '')
                    description = version_info.get('FileDescription', '')
                    return publisher, description
                except json.JSONDecodeError:
                    pass
            
            return "", ""
            
        except Exception:
            return "", ""
    
    def _get_file_modified_date(self, file_path):
        """Get file last modified date."""
        try:
            if os.path.exists(file_path):
                timestamp = os.path.getmtime(file_path)
                return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass
        return ""
    






    def _analyze_startup_impact(self):
        """Analyze the performance impact of startup items."""
        for item in self.startup_items:
            try:
                # Simple heuristic based on file size and known programs
                impact = "Low"
                
                if item.path and os.path.exists(item.path):
                    file_size = os.path.getsize(item.path)
                    
                    # Large files typically have higher impact
                    if file_size > 50 * 1024 * 1024:  # > 50MB
                        impact = "High"
                    elif file_size > 10 * 1024 * 1024:  # > 10MB
                        impact = "Medium"
                
                # Known high-impact programs
                high_impact_programs = [
                    'adobe', 'office', 'skype', 'steam', 'discord', 'spotify',
                    'chrome', 'firefox', 'antivirus', 'backup'
                ]
                
                name_lower = item.name.lower()
                for high_impact in high_impact_programs:
                    if high_impact in name_lower:
                        impact = "High"
                        break
                
                # System programs typically have medium impact
                if item.is_system_critical:
                    impact = "Medium"
                
                item.impact = impact
                
            except Exception:
                item.impact = "Unknown"

    def _is_manageable_item(self, startup_item):
        """Check if a startup item can be safely managed (enabled/disabled)."""
        try:
            # Test if we can actually manage this item
            if startup_item.location.startswith("Registry"):
                # Check if we have registry access
                if "User" in startup_item.location:
                    hkey = winreg.HKEY_CURRENT_USER
                else:
                    hkey = winreg.HKEY_LOCAL_MACHINE

                try:
                    with winreg.OpenKey(hkey, startup_item.registry_key, 0, winreg.KEY_READ) as key:
                        # Try to read the value to ensure it exists and is accessible
                        if startup_item.enabled:
                            winreg.QueryValueEx(key, startup_item.registry_value)
                        else:
                            winreg.QueryValueEx(key, f"{startup_item.registry_value}_DISABLED")
                        return True
                except (FileNotFoundError, PermissionError, OSError):
                    return False

            elif "Startup Folder" in startup_item.location:
                # Check if file exists and is accessible
                return os.path.exists(startup_item.path) or os.path.exists(f"{startup_item.path}.disabled")

            elif startup_item.location == "Windows Service":
                # Check if service exists and can be configured
                try:
                    service_name = self._get_service_name_from_display_name(startup_item.name)
                    result = subprocess.run([
                        'sc', 'qc', service_name
                    ], capture_output=True, text=True, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    return result.returncode == 0
                except Exception:
                    return False

            elif startup_item.location == "Scheduled Task":
                # Check if task exists and can be managed
                try:
                    result = subprocess.run([
                        'schtasks', '/query', '/tn', startup_item.name
                    ], capture_output=True, text=True, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    return result.returncode == 0
                except Exception:
                    return False

            return True

        except Exception:
            return False


class StartupManager:
    """Manages startup programs - enable, disable, backup, restore."""

    def __init__(self):
        self.scanner = StartupScanner()
        self.startup_items = []
        self.backup_data = {}

    def get_startup_items(self, progress_callback=None):
        """Get all startup items."""
        self.startup_items = self.scanner.scan_all_startup_locations(progress_callback)
        return self.startup_items

    def create_backup(self):
        """Create backup of current startup configuration."""
        try:
            backup = {
                "timestamp": datetime.now().isoformat(),
                "items": [item.to_dict() for item in self.startup_items]
            }

            backup_file = f"startup_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup, f, indent=2, ensure_ascii=False)

            self.backup_data = backup
            return True, f"Backup created: {backup_file}"

        except Exception as e:
            return False, f"Failed to create backup: {str(e)}"

    def disable_startup_item(self, item):
        """Disable a startup item."""
        try:
            if item.location.startswith("HKCU") or item.location.startswith("HKLM"):
                return self._disable_registry_item(item)
            elif "Startup Folder" in item.location:
                return self._disable_folder_item(item)
            elif item.location == "Windows Service":
                return self._disable_service_item(item)
            elif item.location == "Scheduled Task":
                return self._disable_task_item(item)
            else:
                return False, f"Unknown startup location: {item.location}"

        except Exception as e:
            return False, f"Error disabling startup item: {str(e)}"

    def enable_startup_item(self, item):
        """Enable a startup item."""
        try:
            if item.location.startswith("HKCU") or item.location.startswith("HKLM"):
                return self._enable_registry_item(item)
            elif "Startup Folder" in item.location:
                return self._enable_folder_item(item)
            elif item.location == "Windows Service":
                return self._enable_service_item(item)
            elif item.location == "Scheduled Task":
                return self._enable_task_item(item)
            else:
                return False, f"Unknown startup location: {item.location}"

        except Exception as e:
            return False, f"Error enabling startup item: {str(e)}"

    def _disable_registry_item(self, item):
        """Disable registry startup item by renaming the value."""
        try:
            # Determine registry hive
            if "User" in item.location:
                hkey = winreg.HKEY_CURRENT_USER
            else:
                hkey = winreg.HKEY_LOCAL_MACHINE

            # Open registry key
            with winreg.OpenKey(hkey, item.registry_key, 0, winreg.KEY_ALL_ACCESS) as key:
                # Get current value
                current_value, reg_type = winreg.QueryValueEx(key, item.registry_value)

                # Rename to disabled (add _DISABLED suffix)
                disabled_name = f"{item.registry_value}_DISABLED"
                winreg.SetValueEx(key, disabled_name, 0, reg_type, current_value)

                # Delete original value
                winreg.DeleteValue(key, item.registry_value)

            item.enabled = False
            return True, f"Disabled {item.name}"

        except Exception as e:
            return False, f"Failed to disable registry item: {str(e)}"

    def _enable_registry_item(self, item):
        """Enable registry startup item by restoring the original value name."""
        try:
            # Determine registry hive
            if "User" in item.location:
                hkey = winreg.HKEY_CURRENT_USER
            else:
                hkey = winreg.HKEY_LOCAL_MACHINE

            # Look for disabled version
            disabled_name = f"{item.registry_value}_DISABLED"

            with winreg.OpenKey(hkey, item.registry_key, 0, winreg.KEY_ALL_ACCESS) as key:
                try:
                    # Get disabled value
                    current_value, reg_type = winreg.QueryValueEx(key, disabled_name)

                    # Restore original name
                    winreg.SetValueEx(key, item.registry_value, 0, reg_type, current_value)

                    # Delete disabled version
                    winreg.DeleteValue(key, disabled_name)

                    item.enabled = True
                    return True, f"Enabled {item.name}"

                except FileNotFoundError:
                    return False, f"Disabled version of {item.name} not found"

        except Exception as e:
            return False, f"Failed to enable registry item: {str(e)}"

    def _disable_folder_item(self, item):
        """Disable startup folder item by renaming file."""
        try:
            disabled_path = f"{item.path}.disabled"
            os.rename(item.path, disabled_path)
            item.enabled = False
            item.path = disabled_path
            return True, f"Disabled {item.name}"

        except Exception as e:
            return False, f"Failed to disable folder item: {str(e)}"

    def _enable_folder_item(self, item):
        """Enable startup folder item by restoring original filename."""
        try:
            if item.path.endswith('.disabled'):
                original_path = item.path[:-9]  # Remove .disabled
                os.rename(item.path, original_path)
                item.enabled = True
                item.path = original_path
                return True, f"Enabled {item.name}"
            else:
                return False, f"{item.name} is not disabled"

        except Exception as e:
            return False, f"Failed to enable folder item: {str(e)}"

    def _disable_service_item(self, item):
        """Disable Windows service (change to manual start)."""
        try:
            # Extract service name from display name if needed
            service_name = self._get_service_name_from_display_name(item.name)

            # Use sc command to change service start type
            result = subprocess.run([
                'sc', 'config', service_name, 'start=demand'
            ], capture_output=True, text=True, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

            if result.returncode == 0:
                item.enabled = False
                return True, f"Changed {item.name} to manual start"
            else:
                return False, f"Failed to change service: {result.stderr}"

        except Exception as e:
            return False, f"Failed to disable service: {str(e)}"

    def _enable_service_item(self, item):
        """Enable Windows service (change to automatic start)."""
        try:
            # Extract service name from display name if needed
            service_name = self._get_service_name_from_display_name(item.name)

            # Use sc command to change service start type
            result = subprocess.run([
                'sc', 'config', service_name, 'start=auto'
            ], capture_output=True, text=True, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

            if result.returncode == 0:
                item.enabled = True
                return True, f"Changed {item.name} to automatic start"
            else:
                return False, f"Failed to change service: {result.stderr}"

        except Exception as e:
            return False, f"Failed to enable service: {str(e)}"

    def _get_service_name_from_display_name(self, display_name):
        """Get the actual service name from display name."""
        try:
            # Try to find the service name using sc query
            result = subprocess.run([
                'sc', 'query', 'state=all'
            ], capture_output=True, text=True, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for i, line in enumerate(lines):
                    if 'DISPLAY_NAME:' in line and display_name in line:
                        # Look for SERVICE_NAME in previous lines
                        for j in range(max(0, i-5), i):
                            if 'SERVICE_NAME:' in lines[j]:
                                service_name = lines[j].split('SERVICE_NAME:')[1].strip()
                                return service_name

            # If not found, return the display name as fallback
            return display_name

        except Exception:
            return display_name

    def _disable_task_item(self, item):
        """Disable scheduled task."""
        try:
            result = subprocess.run([
                'schtasks', '/change', '/tn', item.name, '/disable'
            ], capture_output=True, text=True, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

            if result.returncode == 0:
                item.enabled = False
                return True, f"Disabled task {item.name}"
            else:
                return False, f"Failed to disable task: {result.stderr}"

        except Exception as e:
            return False, f"Failed to disable task: {str(e)}"

    def _enable_task_item(self, item):
        """Enable scheduled task."""
        try:
            result = subprocess.run([
                'schtasks', '/change', '/tn', item.name, '/enable'
            ], capture_output=True, text=True, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

            if result.returncode == 0:
                item.enabled = True
                return True, f"Enabled task {item.name}"
            else:
                return False, f"Failed to enable task: {result.stderr}"

        except Exception as e:
            return False, f"Failed to enable task: {str(e)}"

    def bulk_disable_items(self, items):
        """Disable multiple startup items."""
        results = []
        for item in items:
            success, message = self.disable_startup_item(item)
            results.append((item.name, success, message))
        return results

    def bulk_enable_items(self, items):
        """Enable multiple startup items."""
        results = []
        for item in items:
            success, message = self.enable_startup_item(item)
            results.append((item.name, success, message))
        return results

    def estimate_boot_time_improvement(self, items_to_disable):
        """Estimate boot time improvement from disabling items."""
        try:
            # Simple heuristic based on impact levels
            improvement_seconds = 0

            for item in items_to_disable:
                if item.impact == "High":
                    improvement_seconds += 8  # 8 seconds improvement
                elif item.impact == "Medium":
                    improvement_seconds += 4  # 4 seconds improvement
                elif item.impact == "Low":
                    improvement_seconds += 1  # 1 second improvement

            return improvement_seconds

        except Exception:
            return 0

    def export_startup_config(self, filepath, format_type='json'):
        """Export startup configuration to file."""
        try:
            export_data = {
                "export_info": {
                    "timestamp": datetime.now().isoformat(),
                    "date_readable": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "format_version": "1.0",
                    "total_items": len(self.startup_items)
                },
                "startup_items": [item.to_dict() for item in self.startup_items]
            }

            if format_type.lower() == 'json':
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
            else:  # text format
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("STARTUP PROGRAMS REPORT\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Total Items: {len(self.startup_items)}\n\n")

                    # Group by location
                    locations = {}
                    for item in self.startup_items:
                        if item.location not in locations:
                            locations[item.location] = []
                        locations[item.location].append(item)

                    for location, items in locations.items():
                        f.write(f"{location.upper()}\n")
                        f.write("-" * 30 + "\n")

                        for item in items:
                            f.write(f"Name: {item.name}\n")
                            f.write(f"Status: {'Enabled' if item.enabled else 'Disabled'}\n")
                            f.write(f"Impact: {item.impact}\n")
                            f.write(f"Path: {item.path}\n")
                            if item.publisher:
                                f.write(f"Publisher: {item.publisher}\n")
                            if item.description:
                                f.write(f"Description: {item.description}\n")
                            f.write(f"System Critical: {'Yes' if item.is_system_critical else 'No'}\n")
                            f.write("\n")

                        f.write("\n")

            return True, f"Startup configuration exported to {filepath}"

        except Exception as e:
            return False, f"Error exporting startup configuration: {str(e)}"
