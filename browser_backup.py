#!/usr/bin/env python3
"""
Browser Backup and Restore functionality for Programming Tools Version Checker.
Supports Chrome, Brave, Firefox, Edge, and other Chromium-based browsers.
"""

import os
import shutil
import json
import sqlite3
import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import subprocess

class BrowserBackup:
    """Class for backing up and restoring browser data."""
    
    def __init__(self):
        self.backup_base_path = Path("browser_backups")
        self.backup_base_path.mkdir(exist_ok=True)
        
        # Define browser configurations
        self.browsers = {
            'Chrome': {
                'name': 'Google Chrome',
                'data_path': self._get_chrome_path(),
                'profile_folders': ['Default', 'Profile 1', 'Profile 2', 'Profile 3'],
                'files_to_backup': [
                    'Bookmarks',
                    'History',
                    'Login Data',
                    'Preferences',
                    'Secure Preferences',
                    'Web Data',
                    'Cookies',
                    'Local Storage',
                    'Session Storage',
                    'Extensions'
                ]
            },
            'Brave': {
                'name': 'Brave Browser',
                'data_path': self._get_brave_path(),
                'profile_folders': ['Default', 'Profile 1', 'Profile 2', 'Profile 3'],
                'files_to_backup': [
                    'Bookmarks',
                    'History',
                    'Login Data',
                    'Preferences',
                    'Secure Preferences',
                    'Web Data',
                    'Cookies',
                    'Local Storage',
                    'Session Storage',
                    'Extensions'
                ]
            },
            'Edge': {
                'name': 'Microsoft Edge',
                'data_path': self._get_edge_path(),
                'profile_folders': ['Default', 'Profile 1', 'Profile 2', 'Profile 3'],
                'files_to_backup': [
                    'Bookmarks',
                    'History',
                    'Login Data',
                    'Preferences',
                    'Secure Preferences',
                    'Web Data',
                    'Cookies',
                    'Local Storage',
                    'Session Storage',
                    'Extensions'
                ]
            },
            'Firefox': {
                'name': 'Mozilla Firefox',
                'data_path': self._get_firefox_path(),
                'profile_folders': [],  # Firefox uses different profile structure
                'files_to_backup': [
                    'places.sqlite',  # Bookmarks and history
                    'key4.db',       # Passwords
                    'logins.json',   # Login data
                    'prefs.js',      # Preferences
                    'cookies.sqlite',
                    'formhistory.sqlite',
                    'extensions.json',
                    'addons.json'
                ]
            }
        }
    
    def _get_chrome_path(self) -> Optional[Path]:
        """Get Chrome data path."""
        chrome_paths = [
            Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data",
            Path.home() / ".config" / "google-chrome",  # Linux
            Path.home() / "Library" / "Application Support" / "Google" / "Chrome"  # macOS
        ]
        
        for path in chrome_paths:
            if path.exists():
                return path
        return None
    
    def _get_brave_path(self) -> Optional[Path]:
        """Get Brave data path."""
        brave_paths = [
            Path.home() / "AppData" / "Local" / "BraveSoftware" / "Brave-Browser" / "User Data",
            Path.home() / ".config" / "BraveSoftware" / "Brave-Browser",  # Linux
            Path.home() / "Library" / "Application Support" / "BraveSoftware" / "Brave-Browser"  # macOS
        ]
        
        for path in brave_paths:
            if path.exists():
                return path
        return None
    
    def _get_edge_path(self) -> Optional[Path]:
        """Get Edge data path."""
        edge_paths = [
            Path.home() / "AppData" / "Local" / "Microsoft" / "Edge" / "User Data",
            Path.home() / ".config" / "microsoft-edge",  # Linux
            Path.home() / "Library" / "Application Support" / "Microsoft Edge"  # macOS
        ]
        
        for path in edge_paths:
            if path.exists():
                return path
        return None
    
    def _get_firefox_path(self) -> Optional[Path]:
        """Get Firefox data path."""
        firefox_paths = [
            Path.home() / "AppData" / "Roaming" / "Mozilla" / "Firefox" / "Profiles",
            Path.home() / ".mozilla" / "firefox",  # Linux
            Path.home() / "Library" / "Application Support" / "Firefox" / "Profiles"  # macOS
        ]
        
        for path in firefox_paths:
            if path.exists():
                return path
        return None
    
    def detect_browsers(self) -> Dict[str, bool]:
        """Detect which browsers are installed."""
        detected = {}
        
        for browser_name, config in self.browsers.items():
            data_path = config['data_path']
            detected[browser_name] = data_path is not None and data_path.exists()
        
        return detected
    
    def get_browser_profiles(self, browser_name: str) -> List[str]:
        """Get available profiles for a browser."""
        if browser_name not in self.browsers:
            return []
        
        config = self.browsers[browser_name]
        data_path = config['data_path']
        
        if not data_path or not data_path.exists():
            return []
        
        profiles = []
        
        if browser_name == 'Firefox':
            # Firefox has different profile structure
            try:
                for item in data_path.iterdir():
                    if item.is_dir() and not item.name.startswith('.'):
                        profiles.append(item.name)
            except:
                pass
        else:
            # Chromium-based browsers
            for profile_folder in config['profile_folders']:
                profile_path = data_path / profile_folder
                if profile_path.exists():
                    profiles.append(profile_folder)
        
        return profiles

    def backup_browser(self, browser_name: str, profiles: List[str] = None,
                      progress_callback=None) -> Tuple[bool, str]:
        """
        Backup browser data.

        Args:
            browser_name: Name of the browser to backup
            profiles: List of profiles to backup (None for all)
            progress_callback: Optional callback for progress updates

        Returns:
            Tuple of (success, message/backup_path)
        """
        if browser_name not in self.browsers:
            return False, f"Browser {browser_name} not supported"

        config = self.browsers[browser_name]
        data_path = config['data_path']

        if not data_path or not data_path.exists():
            return False, f"{browser_name} data directory not found"

        # Create backup directory with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.backup_base_path / f"{browser_name}_{timestamp}"
        backup_dir.mkdir(exist_ok=True)

        if progress_callback:
            progress_callback(f"Creating backup directory: {backup_dir}")

        try:
            # Get profiles to backup
            if profiles is None:
                profiles = self.get_browser_profiles(browser_name)

            if not profiles:
                return False, f"No profiles found for {browser_name}"

            total_files = 0
            copied_files = 0

            for profile in profiles:
                if progress_callback:
                    progress_callback(f"Backing up profile: {profile}")

                if browser_name == 'Firefox':
                    profile_source = data_path / profile
                else:
                    profile_source = data_path / profile

                if not profile_source.exists():
                    continue

                profile_backup = backup_dir / profile
                profile_backup.mkdir(exist_ok=True)

                # Backup specific files
                for file_name in config['files_to_backup']:
                    source_file = profile_source / file_name

                    if source_file.exists():
                        total_files += 1
                        try:
                            if source_file.is_file():
                                shutil.copy2(source_file, profile_backup / file_name)
                            elif source_file.is_dir():
                                shutil.copytree(source_file, profile_backup / file_name,
                                              dirs_exist_ok=True)
                            copied_files += 1

                            if progress_callback:
                                progress_callback(f"Copied: {file_name}")

                        except Exception as e:
                            if progress_callback:
                                progress_callback(f"Failed to copy {file_name}: {str(e)}")

            # Create backup info file
            backup_info = {
                'browser': browser_name,
                'timestamp': timestamp,
                'profiles': profiles,
                'total_files': total_files,
                'copied_files': copied_files,
                'backup_date': datetime.datetime.now().isoformat()
            }

            with open(backup_dir / "backup_info.json", 'w') as f:
                json.dump(backup_info, f, indent=2)

            if progress_callback:
                progress_callback(f"Backup completed: {copied_files}/{total_files} files")

            return True, str(backup_dir)

        except Exception as e:
            return False, f"Backup failed: {str(e)}"

    def restore_browser(self, backup_path: str, browser_name: str = None,
                       progress_callback=None) -> Tuple[bool, str]:
        """
        Restore browser data from backup.

        Args:
            backup_path: Path to backup directory
            browser_name: Target browser (None to use original)
            progress_callback: Optional callback for progress updates

        Returns:
            Tuple of (success, message)
        """
        backup_dir = Path(backup_path)

        if not backup_dir.exists():
            return False, f"Backup directory not found: {backup_path}"

        # Read backup info
        backup_info_file = backup_dir / "backup_info.json"
        if not backup_info_file.exists():
            return False, "Backup info file not found"

        try:
            with open(backup_info_file, 'r') as f:
                backup_info = json.load(f)
        except Exception as e:
            return False, f"Failed to read backup info: {str(e)}"

        # Determine target browser
        target_browser = browser_name or backup_info['browser']

        if target_browser not in self.browsers:
            return False, f"Target browser {target_browser} not supported"

        config = self.browsers[target_browser]
        data_path = config['data_path']

        if not data_path:
            return False, f"{target_browser} data directory not found"

        if progress_callback:
            progress_callback(f"Restoring to {target_browser}")

        try:
            restored_files = 0

            for profile in backup_info['profiles']:
                if progress_callback:
                    progress_callback(f"Restoring profile: {profile}")

                profile_backup = backup_dir / profile
                if not profile_backup.exists():
                    continue

                if target_browser == 'Firefox':
                    profile_target = data_path / profile
                else:
                    profile_target = data_path / profile

                profile_target.mkdir(exist_ok=True)

                # Restore files
                for item in profile_backup.iterdir():
                    if item.name == "backup_info.json":
                        continue

                    target_file = profile_target / item.name

                    try:
                        if item.is_file():
                            shutil.copy2(item, target_file)
                        elif item.is_dir():
                            if target_file.exists():
                                shutil.rmtree(target_file)
                            shutil.copytree(item, target_file)

                        restored_files += 1

                        if progress_callback:
                            progress_callback(f"Restored: {item.name}")

                    except Exception as e:
                        if progress_callback:
                            progress_callback(f"Failed to restore {item.name}: {str(e)}")

            if progress_callback:
                progress_callback(f"Restore completed: {restored_files} files restored")

            return True, f"Successfully restored {restored_files} files to {target_browser}"

        except Exception as e:
            return False, f"Restore failed: {str(e)}"

    def list_backups(self) -> List[Dict]:
        """List all available backups."""
        backups = []

        try:
            for backup_dir in self.backup_base_path.iterdir():
                if backup_dir.is_dir():
                    backup_info_file = backup_dir / "backup_info.json"

                    if backup_info_file.exists():
                        try:
                            with open(backup_info_file, 'r') as f:
                                backup_info = json.load(f)

                            backup_info['path'] = str(backup_dir)
                            backup_info['size'] = self._get_directory_size(backup_dir)
                            backups.append(backup_info)

                        except Exception as e:
                            # Add basic info even if backup_info.json is corrupted
                            backups.append({
                                'browser': 'Unknown',
                                'timestamp': backup_dir.name,
                                'path': str(backup_dir),
                                'size': self._get_directory_size(backup_dir),
                                'error': str(e)
                            })
        except Exception:
            pass

        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return backups

    def _get_directory_size(self, path: Path) -> int:
        """Get total size of directory in bytes."""
        total_size = 0
        try:
            for item in path.rglob('*'):
                if item.is_file():
                    total_size += item.stat().st_size
        except Exception:
            pass
        return total_size

    def format_size(self, size_bytes: int) -> str:
        """Format size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def delete_backup(self, backup_path: str) -> Tuple[bool, str]:
        """Delete a backup."""
        backup_dir = Path(backup_path)

        if not backup_dir.exists():
            return False, f"Backup directory not found: {backup_path}"

        try:
            shutil.rmtree(backup_dir)
            return True, f"Backup deleted successfully: {backup_path}"
        except Exception as e:
            return False, f"Failed to delete backup: {str(e)}"

    def export_bookmarks_html(self, browser_name: str, profile: str = "Default") -> Tuple[bool, str]:
        """Export bookmarks to HTML format."""
        if browser_name not in self.browsers:
            return False, f"Browser {browser_name} not supported"

        config = self.browsers[browser_name]
        data_path = config['data_path']

        if not data_path or not data_path.exists():
            return False, f"{browser_name} data directory not found"

        try:
            if browser_name == 'Firefox':
                # Firefox uses places.sqlite
                profile_path = data_path / profile
                places_db = profile_path / "places.sqlite"

                if not places_db.exists():
                    return False, "Firefox bookmarks database not found"

                # Export Firefox bookmarks
                return self._export_firefox_bookmarks_html(places_db)
            else:
                # Chromium-based browsers use Bookmarks file
                profile_path = data_path / profile
                bookmarks_file = profile_path / "Bookmarks"

                if not bookmarks_file.exists():
                    return False, f"{browser_name} bookmarks file not found"

                # Export Chromium bookmarks
                return self._export_chromium_bookmarks_html(bookmarks_file, browser_name)

        except Exception as e:
            return False, f"Failed to export bookmarks: {str(e)}"

    def _export_chromium_bookmarks_html(self, bookmarks_file: Path, browser_name: str) -> Tuple[bool, str]:
        """Export Chromium-based browser bookmarks to HTML."""
        try:
            with open(bookmarks_file, 'r', encoding='utf-8') as f:
                bookmarks_data = json.load(f)

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.backup_base_path / f"{browser_name}_bookmarks_{timestamp}.html"

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('<!DOCTYPE NETSCAPE-Bookmark-file-1>\n')
                f.write('<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n')
                f.write(f'<TITLE>Bookmarks from {browser_name}</TITLE>\n')
                f.write('<H1>Bookmarks</H1>\n')
                f.write('<DL><p>\n')

                # Process bookmark bar
                if 'roots' in bookmarks_data and 'bookmark_bar' in bookmarks_data['roots']:
                    self._write_chromium_folder_html(f, bookmarks_data['roots']['bookmark_bar'], 0)

                # Process other bookmarks
                if 'roots' in bookmarks_data and 'other' in bookmarks_data['roots']:
                    f.write('<DT><H3>Other Bookmarks</H3>\n<DL><p>\n')
                    self._write_chromium_folder_html(f, bookmarks_data['roots']['other'], 1)
                    f.write('</DL><p>\n')

                f.write('</DL><p>\n')

            return True, str(output_file)

        except Exception as e:
            return False, f"Failed to export Chromium bookmarks: {str(e)}"

    def _write_chromium_folder_html(self, f, folder, depth):
        """Write Chromium folder structure to HTML."""
        if 'children' not in folder:
            return

        for item in folder['children']:
            if item['type'] == 'folder':
                f.write(f'<DT><H3>{item["name"]}</H3>\n<DL><p>\n')
                self._write_chromium_folder_html(f, item, depth + 1)
                f.write('</DL><p>\n')
            elif item['type'] == 'url':
                f.write(f'<DT><A HREF="{item["url"]}">{item["name"]}</A>\n')

    def _export_firefox_bookmarks_html(self, places_db: Path) -> Tuple[bool, str]:
        """Export Firefox bookmarks to HTML."""
        try:
            # Copy database to avoid locking issues
            temp_db = places_db.parent / "places_temp.sqlite"
            shutil.copy2(places_db, temp_db)

            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.backup_base_path / f"Firefox_bookmarks_{timestamp}.html"

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('<!DOCTYPE NETSCAPE-Bookmark-file-1>\n')
                f.write('<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n')
                f.write('<TITLE>Bookmarks from Firefox</TITLE>\n')
                f.write('<H1>Bookmarks</H1>\n')
                f.write('<DL><p>\n')

                # Get bookmarks
                cursor.execute("""
                    SELECT b.title, p.url
                    FROM moz_bookmarks b
                    JOIN moz_places p ON b.fk = p.id
                    WHERE b.type = 1 AND p.url IS NOT NULL
                    ORDER BY b.title
                """)

                for title, url in cursor.fetchall():
                    if title and url:
                        f.write(f'<DT><A HREF="{url}">{title}</A>\n')

                f.write('</DL><p>\n')

            conn.close()
            temp_db.unlink()  # Delete temp file

            return True, str(output_file)

        except Exception as e:
            return False, f"Failed to export Firefox bookmarks: {str(e)}"
