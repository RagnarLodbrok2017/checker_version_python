#!/usr/bin/env python3
"""
Hardware Information Viewer Module
Provides comprehensive system hardware information gathering and display functionality.
"""

import subprocess
import json
import platform
import psutil
import threading
import time
from datetime import datetime
import os
import re


class HardwareInfoCollector:
    """Collects comprehensive hardware information from the system."""
    
    def __init__(self):
        self.hardware_data = {}
        self.is_windows = platform.system().lower() == 'windows'
        
    def collect_all_hardware_info(self, progress_callback=None):
        """Collect all hardware information with progress updates."""
        try:
            if progress_callback:
                progress_callback("Collecting system information...", 10)
            self.collect_system_info()
            
            if progress_callback:
                progress_callback("Collecting CPU information...", 25)
            self.collect_cpu_info()
            
            if progress_callback:
                progress_callback("Collecting memory information...", 40)
            self.collect_memory_info()
            
            if progress_callback:
                progress_callback("Collecting GPU information...", 55)
            self.collect_gpu_info()
            
            if progress_callback:
                progress_callback("Collecting storage information...", 70)
            self.collect_storage_info()
            
            if progress_callback:
                progress_callback("Collecting battery information...", 85)
            self.collect_battery_info()
            
            if progress_callback:
                progress_callback("Finalizing hardware information...", 100)
            
            return self.hardware_data
            
        except Exception as e:
            print(f"Error collecting hardware info: {e}")
            return {"error": str(e)}
    
    def collect_system_info(self):
        """Collect system information."""
        try:
            system_info = {}
            
            # Basic system info
            system_info['computer_name'] = platform.node()
            system_info['operating_system'] = f"{platform.system()} {platform.release()}"
            system_info['os_version'] = platform.version()
            system_info['architecture'] = platform.machine()
            
            if self.is_windows:
                # Get detailed Windows info using WMI
                try:
                    # System manufacturer and model
                    wmi_result = self._run_wmi_query("SELECT Manufacturer, Model FROM Win32_ComputerSystem")
                    if wmi_result:
                        system_info['manufacturer'] = wmi_result.get('Manufacturer', 'Unknown')
                        system_info['model'] = wmi_result.get('Model', 'Unknown')
                    
                    # System type detection
                    chassis_result = self._run_wmi_query("SELECT ChassisTypes FROM Win32_SystemEnclosure")
                    if chassis_result and 'ChassisTypes' in chassis_result:
                        chassis_type = chassis_result['ChassisTypes']
                        if isinstance(chassis_type, list) and len(chassis_type) > 0:
                            chassis_type = chassis_type[0]
                        system_info['system_type'] = self._get_system_type_from_chassis(chassis_type)
                    
                    # Windows build info
                    os_result = self._run_wmi_query("SELECT BuildNumber, Version FROM Win32_OperatingSystem")
                    if os_result:
                        system_info['build_number'] = os_result.get('BuildNumber', 'Unknown')
                        system_info['os_detailed_version'] = os_result.get('Version', 'Unknown')
                        
                except Exception as e:
                    print(f"Error getting Windows system info: {e}")
                    system_info['manufacturer'] = 'Unknown'
                    system_info['model'] = 'Unknown'
                    system_info['system_type'] = 'Unknown'
            else:
                system_info['manufacturer'] = 'Unknown'
                system_info['model'] = 'Unknown'
                system_info['system_type'] = 'Unknown'
            
            self.hardware_data['system'] = system_info
            
        except Exception as e:
            print(f"Error collecting system info: {e}")
            self.hardware_data['system'] = {"error": str(e)}
    
    def collect_cpu_info(self):
        """Collect CPU information."""
        try:
            cpu_info = {}
            
            # Basic CPU info using psutil
            cpu_info['logical_cores'] = psutil.cpu_count(logical=True)
            cpu_info['physical_cores'] = psutil.cpu_count(logical=False)
            cpu_info['current_usage'] = psutil.cpu_percent(interval=1)
            
            if self.is_windows:
                try:
                    # Detailed CPU info using WMI
                    wmi_result = self._run_wmi_query("SELECT Name, MaxClockSpeed, Architecture FROM Win32_Processor")
                    if wmi_result:
                        cpu_info['name'] = wmi_result.get('Name', 'Unknown').strip()
                        max_clock = wmi_result.get('MaxClockSpeed', 0)
                        if max_clock:
                            cpu_info['max_clock_speed_ghz'] = round(max_clock / 1000, 2)
                        
                        arch = wmi_result.get('Architecture', 0)
                        cpu_info['architecture'] = self._get_cpu_architecture(arch)
                    
                    # Try to get base clock speed
                    try:
                        freq_info = psutil.cpu_freq()
                        if freq_info:
                            cpu_info['current_frequency_ghz'] = round(freq_info.current / 1000, 2)
                            if hasattr(freq_info, 'min') and freq_info.min:
                                cpu_info['min_frequency_ghz'] = round(freq_info.min / 1000, 2)
                            if hasattr(freq_info, 'max') and freq_info.max:
                                cpu_info['max_frequency_ghz'] = round(freq_info.max / 1000, 2)
                    except:
                        pass
                        
                except Exception as e:
                    print(f"Error getting detailed CPU info: {e}")
                    cpu_info['name'] = platform.processor()
            else:
                cpu_info['name'] = platform.processor()
                cpu_info['architecture'] = platform.machine()
            
            self.hardware_data['cpu'] = cpu_info
            
        except Exception as e:
            print(f"Error collecting CPU info: {e}")
            self.hardware_data['cpu'] = {"error": str(e)}
    
    def collect_memory_info(self):
        """Collect memory information."""
        try:
            memory_info = {}
            
            # Basic memory info using psutil
            memory = psutil.virtual_memory()
            memory_info['total_gb'] = round(memory.total / (1024**3), 2)
            memory_info['used_gb'] = round(memory.used / (1024**3), 2)
            memory_info['available_gb'] = round(memory.available / (1024**3), 2)
            memory_info['used_percentage'] = memory.percent
            memory_info['available_percentage'] = round(100 - memory.percent, 1)
            
            if self.is_windows:
                try:
                    # Detailed memory info using WMI
                    wmi_result = self._run_wmi_query("SELECT Speed, MemoryType FROM Win32_PhysicalMemory")
                    if wmi_result:
                        if isinstance(wmi_result, list) and len(wmi_result) > 0:
                            wmi_result = wmi_result[0]  # Take first memory module
                        
                        speed = wmi_result.get('Speed', 0)
                        if speed:
                            memory_info['speed_mhz'] = speed
                        
                        mem_type = wmi_result.get('MemoryType', 0)
                        memory_info['memory_type'] = self._get_memory_type(mem_type)
                        
                except Exception as e:
                    print(f"Error getting detailed memory info: {e}")
                    memory_info['memory_type'] = 'Unknown'
                    memory_info['speed_mhz'] = 'Unknown'
            
            self.hardware_data['memory'] = memory_info
            
        except Exception as e:
            print(f"Error collecting memory info: {e}")
            self.hardware_data['memory'] = {"error": str(e)}
    
    def collect_gpu_info(self):
        """Collect GPU information."""
        try:
            gpu_info = {}
            
            if self.is_windows:
                try:
                    # GPU info using WMI
                    wmi_result = self._run_wmi_query("SELECT Name, AdapterRAM, DriverVersion FROM Win32_VideoController")
                    if wmi_result:
                        if isinstance(wmi_result, list) and len(wmi_result) > 0:
                            # Take the first dedicated GPU or the primary one
                            primary_gpu = wmi_result[0]
                            for gpu in wmi_result:
                                if gpu.get('Name', '').lower() not in ['microsoft basic display adapter', 'generic pnp monitor']:
                                    primary_gpu = gpu
                                    break
                        else:
                            primary_gpu = wmi_result
                        
                        gpu_info['name'] = primary_gpu.get('Name', 'Unknown')
                        
                        vram = primary_gpu.get('AdapterRAM', 0)
                        if vram and vram > 0:
                            gpu_info['vram_gb'] = round(vram / (1024**3), 2)
                        else:
                            gpu_info['vram_gb'] = 'Unknown'
                        
                        gpu_info['driver_version'] = primary_gpu.get('DriverVersion', 'Unknown')
                    
                    # Display resolution
                    display_result = self._run_wmi_query("SELECT CurrentHorizontalResolution, CurrentVerticalResolution, CurrentRefreshRate FROM Win32_VideoController")
                    if display_result:
                        if isinstance(display_result, list) and len(display_result) > 0:
                            display_result = display_result[0]
                        
                        width = display_result.get('CurrentHorizontalResolution', 0)
                        height = display_result.get('CurrentVerticalResolution', 0)
                        refresh = display_result.get('CurrentRefreshRate', 0)
                        
                        if width and height:
                            gpu_info['display_resolution'] = f"{width}x{height}"
                            if refresh:
                                gpu_info['refresh_rate_hz'] = refresh
                        
                except Exception as e:
                    print(f"Error getting GPU info: {e}")
                    gpu_info['name'] = 'Unknown'
                    gpu_info['vram_gb'] = 'Unknown'
                    gpu_info['driver_version'] = 'Unknown'
            else:
                gpu_info['name'] = 'Unknown'
                gpu_info['vram_gb'] = 'Unknown'
                gpu_info['driver_version'] = 'Unknown'
            
            self.hardware_data['gpu'] = gpu_info
            
        except Exception as e:
            print(f"Error collecting GPU info: {e}")
            self.hardware_data['gpu'] = {"error": str(e)}

    def collect_storage_info(self):
        """Collect storage information."""
        try:
            storage_info = {}
            drives = []

            # Get disk usage for all mounted drives
            disk_partitions = psutil.disk_partitions()

            for partition in disk_partitions:
                try:
                    drive_info = {}
                    drive_info['device'] = partition.device
                    drive_info['mountpoint'] = partition.mountpoint
                    drive_info['filesystem'] = partition.fstype

                    # Get disk usage
                    usage = psutil.disk_usage(partition.mountpoint)
                    drive_info['total_gb'] = round(usage.total / (1024**3), 2)
                    drive_info['used_gb'] = round(usage.used / (1024**3), 2)
                    drive_info['free_gb'] = round(usage.free / (1024**3), 2)
                    drive_info['used_percentage'] = round((usage.used / usage.total) * 100, 1)

                    if self.is_windows:
                        try:
                            # Get drive type using WMI
                            drive_letter = partition.device.replace('\\', '').replace(':', '')
                            wmi_query = f"SELECT MediaType, Size FROM Win32_LogicalDisk WHERE DeviceID='{drive_letter}:'"
                            wmi_result = self._run_wmi_query(wmi_query)
                            if wmi_result:
                                media_type = wmi_result.get('MediaType', 0)
                                drive_info['drive_type'] = self._get_drive_type(media_type)

                            # Try to get physical disk info
                            physical_query = f"SELECT MediaType FROM Win32_PhysicalMedia WHERE Tag LIKE '%{drive_letter}%'"
                            physical_result = self._run_wmi_query(physical_query)
                            if physical_result:
                                drive_info['physical_type'] = 'SSD' if 'SSD' in str(physical_result) else 'HDD'

                        except Exception as e:
                            print(f"Error getting drive type for {partition.device}: {e}")
                            drive_info['drive_type'] = 'Unknown'

                    drives.append(drive_info)

                except Exception as e:
                    print(f"Error getting info for drive {partition.device}: {e}")
                    continue

            storage_info['drives'] = drives

            # Get total storage summary
            total_capacity = sum(drive.get('total_gb', 0) for drive in drives)
            total_used = sum(drive.get('used_gb', 0) for drive in drives)
            total_free = sum(drive.get('free_gb', 0) for drive in drives)

            storage_info['total_capacity_gb'] = round(total_capacity, 2)
            storage_info['total_used_gb'] = round(total_used, 2)
            storage_info['total_free_gb'] = round(total_free, 2)
            if total_capacity > 0:
                storage_info['total_used_percentage'] = round((total_used / total_capacity) * 100, 1)

            self.hardware_data['storage'] = storage_info

        except Exception as e:
            print(f"Error collecting storage info: {e}")
            self.hardware_data['storage'] = {"error": str(e)}

    def collect_battery_info(self):
        """Collect battery information (for laptops)."""
        try:
            battery_info = {}

            # Check if battery exists
            battery = psutil.sensors_battery()
            if battery is not None:
                battery_info['present'] = True
                battery_info['charge_percentage'] = round(battery.percent, 1)
                battery_info['power_plugged'] = battery.power_plugged

                if battery.secsleft != psutil.POWER_TIME_UNLIMITED and battery.secsleft != psutil.POWER_TIME_UNKNOWN:
                    hours = battery.secsleft // 3600
                    minutes = (battery.secsleft % 3600) // 60
                    battery_info['time_remaining'] = f"{hours}h {minutes}m"
                else:
                    battery_info['time_remaining'] = "Unknown" if not battery.power_plugged else "Charging"

                if self.is_windows:
                    try:
                        # Get detailed battery info using WMI
                        wmi_result = self._run_wmi_query("SELECT DesignCapacity, FullChargeCapacity, CycleCount FROM Win32_Battery")
                        if wmi_result:
                            design_capacity = wmi_result.get('DesignCapacity', 0)
                            full_capacity = wmi_result.get('FullChargeCapacity', 0)

                            if design_capacity and full_capacity:
                                battery_health = (full_capacity / design_capacity) * 100
                                battery_info['health_percentage'] = round(battery_health, 1)

                            cycle_count = wmi_result.get('CycleCount', 0)
                            if cycle_count:
                                battery_info['cycle_count'] = cycle_count

                    except Exception as e:
                        print(f"Error getting detailed battery info: {e}")
                        battery_info['health_percentage'] = 'Unknown'
                        battery_info['cycle_count'] = 'Unknown'
            else:
                battery_info['present'] = False
                battery_info['message'] = 'No battery detected (Desktop system)'

            self.hardware_data['battery'] = battery_info

        except Exception as e:
            print(f"Error collecting battery info: {e}")
            self.hardware_data['battery'] = {"error": str(e)}

    def _run_wmi_query(self, query):
        """Run WMI query using PowerShell and return parsed result."""
        try:
            if not self.is_windows:
                return None

            # PowerShell command to run WMI query and output as JSON
            ps_command = [
                "powershell",
                "-ExecutionPolicy", "Bypass",
                "-Command",
                f"Get-WmiObject -Query \"{query}\" | ConvertTo-Json -Depth 3"
            ]

            result = subprocess.run(
                ps_command,
                capture_output=True,
                text=True,
                timeout=10,
                shell=True
            )

            if result.returncode == 0 and result.stdout.strip():
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    # If JSON parsing fails, try to extract basic info
                    return self._parse_wmi_text_output(result.stdout)

            return None

        except Exception as e:
            print(f"Error running WMI query: {e}")
            return None

    def _parse_wmi_text_output(self, output):
        """Parse WMI text output when JSON conversion fails."""
        try:
            result = {}
            lines = output.strip().split('\n')

            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    if value and value != 'null':
                        result[key] = value

            return result if result else None

        except Exception as e:
            print(f"Error parsing WMI text output: {e}")
            return None

    def _get_system_type_from_chassis(self, chassis_type):
        """Convert chassis type number to system type string."""
        chassis_types = {
            1: "Other", 2: "Unknown", 3: "Desktop", 4: "Low Profile Desktop",
            5: "Pizza Box", 6: "Mini Tower", 7: "Tower", 8: "Portable",
            9: "Laptop", 10: "Notebook", 11: "Hand Held", 12: "Docking Station",
            13: "All in One", 14: "Sub Notebook", 15: "Space-saving",
            16: "Lunch Box", 17: "Main Server Chassis", 18: "Expansion Chassis",
            19: "SubChassis", 20: "Bus Expansion Chassis", 21: "Peripheral Chassis",
            22: "RAID Chassis", 23: "Rack Mount Chassis", 24: "Sealed-case PC",
            30: "Tablet", 31: "Convertible", 32: "Detachable"
        }

        try:
            chassis_num = int(chassis_type)
            return chassis_types.get(chassis_num, "Unknown")
        except:
            return "Unknown"

    def _get_cpu_architecture(self, arch_code):
        """Convert CPU architecture code to string."""
        architectures = {
            0: "x86", 1: "MIPS", 2: "Alpha", 3: "PowerPC",
            5: "ARM", 6: "ia64", 9: "x64"
        }

        try:
            arch_num = int(arch_code)
            return architectures.get(arch_num, "Unknown")
        except:
            return "Unknown"

    def _get_memory_type(self, mem_type_code):
        """Convert memory type code to string."""
        memory_types = {
            0: "Unknown", 1: "Other", 2: "DRAM", 3: "Synchronous DRAM",
            4: "Cache DRAM", 5: "EDO", 6: "EDRAM", 7: "VRAM", 8: "SRAM",
            9: "RAM", 10: "ROM", 11: "Flash", 12: "EEPROM", 13: "FEPROM",
            14: "EPROM", 15: "CDRAM", 16: "3DRAM", 17: "SDRAM", 18: "SGRAM",
            19: "RDRAM", 20: "DDR", 21: "DDR2", 22: "DDR2 FB-DIMM",
            24: "DDR3", 25: "FBD2", 26: "DDR4", 27: "LPDDR", 28: "LPDDR2",
            29: "LPDDR3", 30: "LPDDR4", 34: "DDR5"
        }

        try:
            mem_num = int(mem_type_code)
            return memory_types.get(mem_num, "Unknown")
        except:
            return "Unknown"

    def _get_drive_type(self, media_type_code):
        """Convert drive media type code to string."""
        drive_types = {
            0: "Unknown", 1: "5.25\" Floppy", 2: "3.5\" Floppy", 3: "3.5\" Floppy",
            4: "3.5\" Floppy", 5: "3.5\" Floppy", 6: "5.25\" Floppy", 7: "5.25\" Floppy",
            8: "5.25\" Floppy", 9: "5.25\" Floppy", 10: "Removable media other than floppy",
            11: "Fixed hard disk", 12: "Removable hard disk", 13: "CD-ROM", 14: "CD-R, CD-RW",
            15: "DVD", 16: "DVD-R, DVD-RW", 17: "DVD-RAM", 18: "DVD+R, DVD+RW",
            19: "Super floppy", 20: "Removable media other than floppy", 21: "Hard disk",
            22: "Optical disk"
        }

        try:
            drive_num = int(media_type_code)
            drive_type = drive_types.get(drive_num, "Unknown")

            # Simplify common types
            if "hard disk" in drive_type.lower() or drive_num == 11:
                return "HDD"
            elif "cd" in drive_type.lower() or "dvd" in drive_type.lower():
                return "Optical"
            elif "floppy" in drive_type.lower():
                return "Floppy"
            else:
                return drive_type

        except:
            return "Unknown"

    def export_to_json(self, filepath):
        """Export hardware information to JSON file."""
        try:
            export_data = {
                "export_info": {
                    "timestamp": datetime.now().isoformat(),
                    "date_readable": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "format_version": "1.0"
                },
                "hardware_information": self.hardware_data
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            return True, f"Hardware information exported to {filepath}"

        except Exception as e:
            return False, f"Error exporting to JSON: {str(e)}"

    def export_to_text(self, filepath):
        """Export hardware information to human-readable text file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("HARDWARE INFORMATION REPORT\n")
                f.write("=" * 50 + "\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                # System Information
                if 'system' in self.hardware_data:
                    f.write("SYSTEM INFORMATION\n")
                    f.write("-" * 30 + "\n")
                    system = self.hardware_data['system']
                    f.write(f"Computer Name: {system.get('computer_name', 'Unknown')}\n")
                    f.write(f"Manufacturer: {system.get('manufacturer', 'Unknown')}\n")
                    f.write(f"Model: {system.get('model', 'Unknown')}\n")
                    f.write(f"System Type: {system.get('system_type', 'Unknown')}\n")
                    f.write(f"Operating System: {system.get('operating_system', 'Unknown')}\n")
                    f.write(f"OS Version: {system.get('os_version', 'Unknown')}\n")
                    f.write(f"Architecture: {system.get('architecture', 'Unknown')}\n\n")

                # CPU Information
                if 'cpu' in self.hardware_data:
                    f.write("CPU INFORMATION\n")
                    f.write("-" * 30 + "\n")
                    cpu = self.hardware_data['cpu']
                    f.write(f"Processor: {cpu.get('name', 'Unknown')}\n")
                    f.write(f"Physical Cores: {cpu.get('physical_cores', 'Unknown')}\n")
                    f.write(f"Logical Cores: {cpu.get('logical_cores', 'Unknown')}\n")
                    f.write(f"Architecture: {cpu.get('architecture', 'Unknown')}\n")
                    f.write(f"Current Usage: {cpu.get('current_usage', 'Unknown')}%\n")
                    if 'max_clock_speed_ghz' in cpu:
                        f.write(f"Max Clock Speed: {cpu['max_clock_speed_ghz']} GHz\n")
                    if 'current_frequency_ghz' in cpu:
                        f.write(f"Current Frequency: {cpu['current_frequency_ghz']} GHz\n")
                    f.write("\n")

                # Memory Information
                if 'memory' in self.hardware_data:
                    f.write("MEMORY INFORMATION\n")
                    f.write("-" * 30 + "\n")
                    memory = self.hardware_data['memory']
                    f.write(f"Total RAM: {memory.get('total_gb', 'Unknown')} GB\n")
                    f.write(f"Used RAM: {memory.get('used_gb', 'Unknown')} GB ({memory.get('used_percentage', 'Unknown')}%)\n")
                    f.write(f"Available RAM: {memory.get('available_gb', 'Unknown')} GB ({memory.get('available_percentage', 'Unknown')}%)\n")
                    f.write(f"Memory Type: {memory.get('memory_type', 'Unknown')}\n")
                    if 'speed_mhz' in memory:
                        f.write(f"Memory Speed: {memory['speed_mhz']} MHz\n")
                    f.write("\n")

                # GPU Information
                if 'gpu' in self.hardware_data:
                    f.write("GPU INFORMATION\n")
                    f.write("-" * 30 + "\n")
                    gpu = self.hardware_data['gpu']
                    f.write(f"Graphics Card: {gpu.get('name', 'Unknown')}\n")
                    f.write(f"Video Memory: {gpu.get('vram_gb', 'Unknown')} GB\n")
                    f.write(f"Driver Version: {gpu.get('driver_version', 'Unknown')}\n")
                    if 'display_resolution' in gpu:
                        f.write(f"Display Resolution: {gpu['display_resolution']}\n")
                    if 'refresh_rate_hz' in gpu:
                        f.write(f"Refresh Rate: {gpu['refresh_rate_hz']} Hz\n")
                    f.write("\n")

                # Storage Information
                if 'storage' in self.hardware_data:
                    f.write("STORAGE INFORMATION\n")
                    f.write("-" * 30 + "\n")
                    storage = self.hardware_data['storage']
                    f.write(f"Total Storage: {storage.get('total_capacity_gb', 'Unknown')} GB\n")
                    f.write(f"Used Storage: {storage.get('total_used_gb', 'Unknown')} GB ({storage.get('total_used_percentage', 'Unknown')}%)\n")
                    f.write(f"Free Storage: {storage.get('total_free_gb', 'Unknown')} GB\n\n")

                    if 'drives' in storage:
                        f.write("INDIVIDUAL DRIVES:\n")
                        for i, drive in enumerate(storage['drives'], 1):
                            f.write(f"  Drive {i}: {drive.get('device', 'Unknown')}\n")
                            f.write(f"    Type: {drive.get('drive_type', 'Unknown')}\n")
                            f.write(f"    Filesystem: {drive.get('filesystem', 'Unknown')}\n")
                            f.write(f"    Total: {drive.get('total_gb', 'Unknown')} GB\n")
                            f.write(f"    Used: {drive.get('used_gb', 'Unknown')} GB ({drive.get('used_percentage', 'Unknown')}%)\n")
                            f.write(f"    Free: {drive.get('free_gb', 'Unknown')} GB\n\n")

                # Battery Information
                if 'battery' in self.hardware_data:
                    f.write("BATTERY INFORMATION\n")
                    f.write("-" * 30 + "\n")
                    battery = self.hardware_data['battery']
                    if battery.get('present', False):
                        f.write(f"Battery Present: Yes\n")
                        f.write(f"Charge Level: {battery.get('charge_percentage', 'Unknown')}%\n")
                        f.write(f"Power Adapter: {'Connected' if battery.get('power_plugged', False) else 'Disconnected'}\n")
                        f.write(f"Time Remaining: {battery.get('time_remaining', 'Unknown')}\n")
                        if 'health_percentage' in battery:
                            f.write(f"Battery Health: {battery['health_percentage']}%\n")
                        if 'cycle_count' in battery:
                            f.write(f"Cycle Count: {battery['cycle_count']}\n")
                    else:
                        f.write("Battery Present: No (Desktop system)\n")
                    f.write("\n")

                f.write("=" * 50 + "\n")
                f.write("End of Hardware Information Report\n")

            return True, f"Hardware information exported to {filepath}"

        except Exception as e:
            return False, f"Error exporting to text: {str(e)}"


class HardwareInfoManager:
    """Manager class for hardware information operations."""

    def __init__(self):
        self.collector = HardwareInfoCollector()
        self.current_data = None

    def collect_hardware_info_async(self, progress_callback=None, completion_callback=None):
        """Collect hardware information in a background thread."""
        def collect_thread():
            try:
                data = self.collector.collect_all_hardware_info(progress_callback)
                self.current_data = data
                if completion_callback:
                    completion_callback(True, data)
            except Exception as e:
                if completion_callback:
                    completion_callback(False, str(e))

        thread = threading.Thread(target=collect_thread, daemon=True)
        thread.start()
        return thread

    def get_current_data(self):
        """Get the currently collected hardware data."""
        return self.current_data

    def export_data(self, filepath, format_type='json'):
        """Export current hardware data to file."""
        if not self.current_data:
            return False, "No hardware data available. Please collect data first."

        if format_type.lower() == 'json':
            return self.collector.export_to_json(filepath)
        elif format_type.lower() == 'text':
            return self.collector.export_to_text(filepath)
        else:
            return False, f"Unsupported format: {format_type}"
