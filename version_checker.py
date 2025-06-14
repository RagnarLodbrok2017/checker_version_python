import subprocess
import sys
import json
from typing import Dict, List, Tuple

class VersionChecker:
    """Core class for checking versions of programming tools and languages."""

    def __init__(self):
        # Define installable tools with their installation commands
        self.installable_tools = {
            # Languages
            'Python': {
                'winget': ['winget', 'install', 'Python.Python.3.12'],
                'chocolatey': ['choco', 'install', 'python', '-y'],
                'description': 'Python programming language'
            },
            'Node.js': {
                'winget': ['winget', 'install', 'OpenJS.NodeJS'],
                'chocolatey': ['choco', 'install', 'nodejs', '-y'],
                'description': 'Node.js JavaScript runtime'
            },
            'Go': {
                'winget': ['winget', 'install', 'GoLang.Go'],
                'chocolatey': ['choco', 'install', 'golang', '-y'],
                'description': 'Go programming language'
            },
            'Rust': {
                'winget': ['winget', 'install', 'Rustlang.Rustup'],
                'chocolatey': ['choco', 'install', 'rust', '-y'],
                'description': 'Rust programming language'
            },
            # Development Tools
            'Git': {
                'winget': ['winget', 'install', 'Git.Git'],
                'chocolatey': ['choco', 'install', 'git', '-y'],
                'description': 'Git version control system'
            },
            'Docker': {
                'winget': ['winget', 'install', 'Docker.DockerDesktop'],
                'chocolatey': ['choco', 'install', 'docker-desktop', '-y'],
                'description': 'Docker containerization platform'
            },
            # Package Managers (npm-based)
            'Yarn': {
                'npm': ['npm', 'install', '-g', 'yarn'],
                'description': 'Yarn package manager'
            },
            'pnpm': {
                'npm': ['npm', 'install', '-g', 'pnpm'],
                'description': 'pnpm package manager'
            },
            # Frontend Tools (npm-based)
            'Vue CLI': {
                'npm': ['npm', 'install', '-g', '@vue/cli'],
                'description': 'Vue.js command line interface'
            },
            'Angular CLI': {
                'npm': ['npm', 'install', '-g', '@angular/cli'],
                'description': 'Angular command line interface'
            },
            'TypeScript': {
                'npm': ['npm', 'install', '-g', 'typescript'],
                'description': 'TypeScript programming language'
            },
        }
        self.tools = {
            'Languages': {
                'Python': ['python', '--version'],
                'Node.js': ['node', '--version'],
                'PHP': ['php', '--version'],
                'Java': ['java', '--version'],
                'Go': ['go', 'version'],
                'Rust': ['rustc', '--version'],
                'Ruby': ['ruby', '--version'],
                'C# (dotnet)': ['dotnet', '--version'],
            },
            'Package Managers': {
                'npm': ['npm', '--version'],
                'pip': ['pip', '--version'],
                'Composer': ['composer', '--version'],
                'Yarn': ['yarn', '--version'],
                'pnpm': ['pnpm', '--version'],
                'Cargo': ['cargo', '--version'],
                'gem': ['gem', '--version'],
                'Maven': ['mvn', '--version'],
                'Gradle': ['gradle', '--version'],
            },
            'Frontend Tools': {
                'Vue CLI': ['vue', '--version'],
                'Angular CLI': ['ng', '--version'],
                'Vite': ['vite', '--version'],
                'Webpack': ['webpack', '--version'],
                'TypeScript': ['tsc', '--version'],
            },
            'Version Control': {
                'Git': ['git', '--version'],
                'SVN': ['svn', '--version'],
            },
            'Databases': {
                'MySQL': ['mysql', '--version'],
                'PostgreSQL': ['psql', '--version'],
                'MongoDB': ['mongo', '--version'],
                'SQLite': ['sqlite3', '--version'],
            },
            'Development Tools': {
                'Docker': ['docker', '--version'],
                'Docker Compose': ['docker-compose', '--version'],
                'VS Code': ['code', '--version'],
                'Cursor': ['cursor', '--version'],
                'Windsurf': ['windsurf', '--version'],
                'Postman': ['postman', '--version'],
            },
            'Development Environments': {
                'WAMP Server': ['wamp_detect'],
                'XAMPP': ['xampp_detect'],
            },
            'Cloud Tools': {
                'AWS CLI': ['aws', '--version'],
                'Azure CLI': ['az', '--version'],
                'Google Cloud SDK': ['gcloud', '--version'],
                'Heroku CLI': ['heroku', '--version'],
            }
        }
    
    def check_single_version(self, command: List[str]) -> Tuple[bool, str]:
        """
        Check version of a single tool.

        Args:
            command: List of command parts to execute

        Returns:
            Tuple of (success, version_string)
        """
        # First try the standard command
        success, version = self._try_command(command)
        if success:
            return True, version

        # Try alternative detection methods for specific tools
        tool_name = command[0].lower()
        if tool_name == 'mysql':
            return self._check_mysql_alternative()
        elif tool_name == 'composer':
            return self._check_composer_alternative()
        elif tool_name == 'wamp_detect':
            return self._check_wamp_installation()
        elif tool_name == 'xampp_detect':
            return self._check_xampp_installation()

        return False, version  # Return the original error message

    def _try_command(self, command: List[str]) -> Tuple[bool, str]:
        """Try to execute a command and get version info."""
        try:
            # Skip problematic commands that might hang
            if command[0] in ['npx'] and len(command) > 2:
                # Skip npx commands that might prompt for installation
                return False, "Skipped (interactive)"

            # Use shell=True for Windows compatibility
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=5,  # Reduced timeout to 5 seconds
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )

            if result.returncode == 0:
                # Clean up the output
                version = result.stdout.strip()
                if not version and result.stderr.strip():
                    version = result.stderr.strip()

                # Extract version number from common patterns
                version = self._extract_version(version)
                return True, version
            else:
                # Some tools return version info in stderr even with non-zero exit
                if result.stderr.strip():
                    stderr_output = result.stderr.strip()
                    if any(word in stderr_output.lower() for word in ['version', 'v']):
                        version = self._extract_version(stderr_output)
                        return True, version
                return False, "Not installed"

        except subprocess.TimeoutExpired:
            return False, "Timeout (5s)"
        except FileNotFoundError:
            return False, "Not found"
        except PermissionError:
            return False, "Permission denied"
        except Exception as e:
            return False, f"Error: {str(e)[:50]}"

    def _check_mysql_alternative(self) -> Tuple[bool, str]:
        """Alternative MySQL detection methods."""
        import os
        import glob

        # Common MySQL installation paths on Windows
        mysql_base_paths = [
            r"C:\Program Files\MySQL\MySQL Server *\bin\mysql.exe",
            r"C:\Program Files (x86)\MySQL\MySQL Server *\bin\mysql.exe",
            r"C:\xampp\mysql\bin\mysql.exe",
            r"C:\wamp64\bin\mysql\mysql*\bin\mysql.exe",
            r"C:\wamp\bin\mysql\mysql*\bin\mysql.exe",
            r"C:\laragon\bin\mysql\mysql*\bin\mysql.exe",
            r"C:\AppServ\MySQL\bin\mysql.exe",
        ]

        # Try glob patterns to find MySQL installations
        for pattern in mysql_base_paths:
            matches = glob.glob(pattern)
            for mysql_path in matches:
                if os.path.exists(mysql_path):
                    success, version = self._try_command([mysql_path, '--version'])
                    if success:
                        return True, version

        # Try to find MySQL through Windows registry or services
        try:
            # Check if MySQL service is running
            result = subprocess.run(
                ['sc', 'query', 'MySQL80'],
                capture_output=True,
                text=True,
                timeout=3,
                shell=True
            )
            if result.returncode == 0 and 'RUNNING' in result.stdout:
                return True, "MySQL Service Running (version unknown)"
        except:
            pass

        return False, "Not found in common locations"

    def _check_composer_alternative(self) -> Tuple[bool, str]:
        """Alternative Composer detection methods."""
        # Try composer.phar
        alternatives = [
            ['composer.phar', '--version'],
            ['php', 'composer.phar', '--version'],
        ]

        for alt_command in alternatives:
            success, version = self._try_command(alt_command)
            if success:
                return True, version

        return False, "Not found"

    def _check_wamp_installation(self) -> Tuple[bool, str]:
        """Detect WAMP Server installation and version."""
        import os
        import glob
        import re

        # Common WAMP installation paths
        wamp_base_paths = [
            r"C:\wamp64",
            r"C:\wamp",
            r"D:\wamp64",
            r"D:\wamp",
            r"C:\Program Files\WampServer",
            r"C:\Program Files (x86)\WampServer",
        ]

        for wamp_path in wamp_base_paths:
            if os.path.exists(wamp_path):
                # Try to get version from various sources
                version = self._get_wamp_version(wamp_path)
                if version:
                    return True, f"WAMP Server {version} (at {wamp_path})"

        # Try to find WAMP through registry or services
        try:
            # Check for WAMP service
            result = subprocess.run(
                ['sc', 'query', 'wampapache64'],
                capture_output=True,
                text=True,
                timeout=3,
                shell=True
            )
            if result.returncode == 0:
                return True, "WAMP Server (service detected, version unknown)"
        except:
            pass

        return False, "Not found"

    def _get_wamp_version(self, wamp_path: str) -> str:
        """Extract WAMP version from installation directory."""
        import os
        import re

        # Method 1: Check for version in directory name or files
        version_patterns = [
            # Look for version in wampmanager.exe properties or nearby files
            os.path.join(wamp_path, "wampmanager.exe"),
            os.path.join(wamp_path, "readme.txt"),
            os.path.join(wamp_path, "VERSION"),
            os.path.join(wamp_path, "CHANGELOG"),
        ]

        for file_path in version_patterns:
            if os.path.exists(file_path):
                try:
                    if file_path.endswith('.exe'):
                        # Try to get version from executable
                        result = subprocess.run(
                            ['powershell', '-Command',
                             f'(Get-ItemProperty "{file_path}").VersionInfo.FileVersion'],
                            capture_output=True,
                            text=True,
                            timeout=3,
                            shell=True
                        )
                        if result.returncode == 0 and result.stdout.strip():
                            return result.stdout.strip()
                    else:
                        # Try to read version from text files
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read(1000)  # Read first 1000 chars
                            # Look for version patterns
                            version_match = re.search(r'(?:version|v\.?)\s*:?\s*(\d+\.\d+(?:\.\d+)?)', content, re.IGNORECASE)
                            if version_match:
                                return version_match.group(1)
                except:
                    continue

        # Method 2: Check Apache version in WAMP (common indicator)
        apache_path = os.path.join(wamp_path, "bin", "apache")
        if os.path.exists(apache_path):
            apache_dirs = [d for d in os.listdir(apache_path) if os.path.isdir(os.path.join(apache_path, d))]
            if apache_dirs:
                # Use the Apache version as an indicator
                apache_version = apache_dirs[0] if apache_dirs else "unknown"
                return f"with Apache {apache_version}"

        # Method 3: Check for WAMP-specific files
        if os.path.exists(os.path.join(wamp_path, "wampmanager.exe")):
            return "detected"

        return ""

    def _check_xampp_installation(self) -> Tuple[bool, str]:
        """Detect XAMPP installation and version."""
        import os
        import re

        # Common XAMPP installation paths
        xampp_base_paths = [
            r"C:\xampp",
            r"D:\xampp",
            r"C:\Program Files\XAMPP",
            r"C:\Program Files (x86)\XAMPP",
        ]

        for xampp_path in xampp_base_paths:
            if os.path.exists(xampp_path):
                # Try to get version from various sources
                version = self._get_xampp_version(xampp_path)
                if version:
                    return True, f"XAMPP {version} (at {xampp_path})"

        # Try to find XAMPP through services
        try:
            # Check for XAMPP Apache service
            result = subprocess.run(
                ['sc', 'query', 'Apache2.4'],
                capture_output=True,
                text=True,
                timeout=3,
                shell=True
            )
            if result.returncode == 0 and 'xampp' in result.stdout.lower():
                return True, "XAMPP (service detected, version unknown)"
        except:
            pass

        return False, "Not found"

    def _get_xampp_version(self, xampp_path: str) -> str:
        """Extract XAMPP version from installation directory."""
        import os
        import re

        # Method 1: Check xampp-control.exe version
        control_exe = os.path.join(xampp_path, "xampp-control.exe")
        if os.path.exists(control_exe):
            try:
                result = subprocess.run(
                    ['powershell', '-Command',
                     f'(Get-ItemProperty "{control_exe}").VersionInfo.FileVersion'],
                    capture_output=True,
                    text=True,
                    timeout=3,
                    shell=True
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except:
                pass

        # Method 2: Check readme files for version
        version_files = [
            os.path.join(xampp_path, "readme_en.txt"),
            os.path.join(xampp_path, "readme_de.txt"),
            os.path.join(xampp_path, "CHANGELOG"),
            os.path.join(xampp_path, "VERSION"),
        ]

        for file_path in version_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(2000)  # Read first 2000 chars
                        # Look for XAMPP version patterns
                        version_patterns = [
                            r'XAMPP\s+(?:for\s+Windows\s+)?(\d+\.\d+\.\d+)',
                            r'Version\s+(\d+\.\d+\.\d+)',
                            r'v\.?\s*(\d+\.\d+\.\d+)',
                        ]
                        for pattern in version_patterns:
                            version_match = re.search(pattern, content, re.IGNORECASE)
                            if version_match:
                                return version_match.group(1)
                except:
                    continue

        # Method 3: Check Apache version in XAMPP (common indicator)
        apache_path = os.path.join(xampp_path, "apache", "bin", "httpd.exe")
        if os.path.exists(apache_path):
            try:
                result = subprocess.run(
                    [apache_path, '-v'],
                    capture_output=True,
                    text=True,
                    timeout=3,
                    shell=True
                )
                if result.returncode == 0:
                    # Extract Apache version as indicator
                    apache_match = re.search(r'Apache/(\d+\.\d+\.\d+)', result.stdout)
                    if apache_match:
                        return f"with Apache {apache_match.group(1)}"
            except:
                pass

        # Method 4: Check for XAMPP-specific files
        if os.path.exists(os.path.join(xampp_path, "xampp-control.exe")):
            return "detected"

        return ""

    def is_tool_installable(self, tool_name: str) -> bool:
        """Check if a tool can be automatically installed."""
        return tool_name in self.installable_tools

    def get_install_description(self, tool_name: str) -> str:
        """Get description for installable tool."""
        if tool_name in self.installable_tools:
            return self.installable_tools[tool_name]['description']
        return ""

    def check_package_managers(self) -> Dict[str, bool]:
        """Check which package managers are available for installation."""
        managers = {}

        # Check winget
        try:
            result = subprocess.run(
                ['winget', '--version'],
                capture_output=True,
                text=True,
                timeout=5,
                shell=True
            )
            managers['winget'] = result.returncode == 0
        except:
            managers['winget'] = False

        # Check chocolatey
        try:
            result = subprocess.run(
                ['choco', '--version'],
                capture_output=True,
                text=True,
                timeout=5,
                shell=True
            )
            managers['chocolatey'] = result.returncode == 0
        except:
            managers['chocolatey'] = False

        # Check npm (for npm-based installations)
        try:
            result = subprocess.run(
                ['npm', '--version'],
                capture_output=True,
                text=True,
                timeout=5,
                shell=True
            )
            managers['npm'] = result.returncode == 0
        except:
            managers['npm'] = False

        return managers

    def install_tool(self, tool_name: str, progress_callback=None, specific_version=None) -> Tuple[bool, str]:
        """
        Install a tool using available package managers.

        Args:
            tool_name: Name of the tool to install
            progress_callback: Optional callback for progress updates
            specific_version: Optional specific version to install

        Returns:
            Tuple of (success, message)
        """
        
    def uninstall_tool(self, tool_name: str, progress_callback=None) -> Tuple[bool, str]:
        """
        Uninstall a tool using available package managers.

        Args:
            tool_name: Name of the tool to uninstall
            progress_callback: Optional callback for progress updates

        Returns:
            Tuple of (success, message)
        """
        if tool_name not in self.installable_tools:
            return False, f"{tool_name} is not in the list of tools that can be managed"

        if progress_callback:
            progress_callback(f"Checking available package managers...")

        # Check available package managers
        available_managers = self.check_package_managers()
        tool_config = self.installable_tools[tool_name]

        # Try uninstallation methods in order of preference
        uninstall_methods = []

        if 'winget' in tool_config and available_managers.get('winget', False):
            # Create uninstall command based on winget install command
            winget_cmd = tool_config['winget'].copy()
            # Replace 'install' with 'uninstall'
            if 'install' in winget_cmd:
                idx = winget_cmd.index('install')
                winget_cmd[idx] = 'uninstall'
                # Add --purge flag for complete removal
                winget_cmd.append('--purge')
                uninstall_methods.append(('winget', winget_cmd))

        if 'npm' in tool_config and available_managers.get('npm', False):
            # Create uninstall command based on npm install command
            npm_cmd = tool_config['npm'].copy()
            # Replace 'install' with 'uninstall'
            if 'install' in npm_cmd:
                idx = npm_cmd.index('install')
                npm_cmd[idx] = 'uninstall'
                uninstall_methods.append(('npm', npm_cmd))

        if 'chocolatey' in tool_config and available_managers.get('chocolatey', False):
            # Create uninstall command based on chocolatey install command
            choco_cmd = tool_config['chocolatey'].copy()
            # Replace 'install' with 'uninstall'
            if 'install' in choco_cmd:
                idx = choco_cmd.index('install')
                choco_cmd[idx] = 'uninstall'
                # Add -y flag for confirmation
                if '-y' not in choco_cmd:
                    choco_cmd.append('-y')
                uninstall_methods.append(('chocolatey', choco_cmd))

        if not uninstall_methods:
            return False, f"No suitable package manager found for uninstalling {tool_name}."

        # Try each uninstallation method
        for method_name, command in uninstall_methods:
            if progress_callback:
                progress_callback(f"Uninstalling {tool_name} using {method_name}...")

            try:
                # Run uninstallation command
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minutes timeout for uninstallation
                    shell=True
                )

                if result.returncode == 0:
                    if progress_callback:
                        progress_callback(f"Successfully uninstalled {tool_name}")
                    return True, f"Successfully uninstalled {tool_name} using {method_name}"
                else:
                    error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
                    if progress_callback:
                        progress_callback(f"Failed to uninstall {tool_name} using {method_name}: {error_msg[:100]}")

                    # Continue to next method if this one failed
                    continue

            except subprocess.TimeoutExpired:
                if progress_callback:
                    progress_callback(f"Uninstallation of {tool_name} timed out")
                return False, f"Uninstallation of {tool_name} timed out (5 minutes)"
            except Exception as e:
                if progress_callback:
                    progress_callback(f"Error uninstalling {tool_name}: {str(e)}")
                continue

        return False, f"Failed to uninstall {tool_name} using all available methods"
        
    def install_tool(self, tool_name: str, progress_callback=None, specific_version=None) -> Tuple[bool, str]:
        """
        Install a tool using available package managers.

        Args:
            tool_name: Name of the tool to install
            progress_callback: Optional callback for progress updates
            specific_version: Optional specific version to install

        Returns:
            Tuple of (success, message)
        """
        if tool_name not in self.installable_tools:
            return False, f"{tool_name} is not in the list of installable tools"

        if progress_callback:
            progress_callback(f"Checking available package managers...")
            
        # Validate the version string if provided
        if specific_version:
            # Check if the version is just the string "version" or other invalid values
            if specific_version.lower() == "version" or not specific_version.strip():
                # Invalid version string, set to None to use default version
                if progress_callback:
                    progress_callback(f"Invalid version '{specific_version}' specified, using latest version instead")
                specific_version = None

        # Check available package managers
        available_managers = self.check_package_managers()
        tool_config = self.installable_tools[tool_name]

        # Try installation methods in order of preference
        install_methods = []

        # Modify commands to include specific version if provided
        if 'winget' in tool_config and available_managers.get('winget', False):
            command = tool_config['winget'].copy()
            if specific_version:
                # Add version parameter for winget
                command.extend(['--version', specific_version])
            install_methods.append(('winget', command))

        if 'npm' in tool_config and available_managers.get('npm', False):
            command = tool_config['npm'].copy()
            if specific_version:
                # For npm, modify the package name to include version
                package_index = -1
                for i, arg in enumerate(command):
                    if i > 0 and arg not in ['-g', '--global']:
                        package_index = i
                        break
                if package_index >= 0:
                    command[package_index] = f"{command[package_index]}@{specific_version}"
            install_methods.append(('npm', command))

        if 'chocolatey' in tool_config and available_managers.get('chocolatey', False):
            command = tool_config['chocolatey'].copy()
            if specific_version:
                # Add version parameter for chocolatey
                command.extend(['--version', specific_version])
            install_methods.append(('chocolatey', command))

        if not install_methods:
            return False, f"No suitable package manager found for {tool_name}. Please install winget, chocolatey, or npm first."

        # Try each installation method
        for method_name, command in install_methods:
            version_text = f" (version {specific_version})" if specific_version else ""
            if progress_callback:
                progress_callback(f"Installing {tool_name}{version_text} using {method_name}...")

            try:
                # Run installation command
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minutes timeout for installation
                    shell=True
                )

                if result.returncode == 0:
                    if progress_callback:
                        progress_callback(f"Successfully installed {tool_name}{version_text}")
                    return True, f"Successfully installed {tool_name}{version_text} using {method_name}"
                else:
                    error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
                    if progress_callback:
                        progress_callback(f"Failed to install {tool_name}{version_text} using {method_name}: {error_msg[:100]}")

                    # Continue to next method if this one failed
                    continue

            except subprocess.TimeoutExpired:
                if progress_callback:
                    progress_callback(f"Installation of {tool_name}{version_text} timed out")
                return False, f"Installation of {tool_name}{version_text} timed out (5 minutes)"
            except Exception as e:
                if progress_callback:
                    progress_callback(f"Error installing {tool_name}{version_text}: {str(e)}")
                continue

        return False, f"Failed to install {tool_name}{version_text} using all available methods"

    def _extract_version(self, version_output: str) -> str:
        """Extract clean version number from command output."""
        lines = version_output.split('\n')
        first_line = lines[0].strip()

        # Handle specific tool patterns
        if first_line.lower().startswith('python'):
            return first_line
        elif first_line.lower().startswith('composer version'):
            return first_line.split('\n')[0]  # Just the first line for Composer
        elif first_line.startswith('v'):
            return first_line
        elif 'version' in first_line.lower():
            return first_line
        elif first_line and len(first_line.split('.')) >= 2:
            # Looks like a version number (e.g., "1.2.3")
            return f"Version {first_line}"
        else:
            # Take first line and limit length
            return first_line[:100] if len(first_line) > 100 else first_line
    
    def check_all_versions(self, progress_callback=None) -> Dict[str, Dict[str, str]]:
        """
        Check versions of all configured tools.

        Args:
            progress_callback: Optional callback function to report progress

        Returns:
            Dictionary organized by category with tool versions
        """
        results = {}
        total_tools = sum(len(tools) for tools in self.tools.values())
        current_tool = 0

        for category, tools in self.tools.items():
            results[category] = {}
            for tool_name, command in tools.items():
                current_tool += 1

                # Report progress if callback provided
                if progress_callback:
                    progress_callback(current_tool, total_tools, tool_name)

                try:
                    success, version = self.check_single_version(command)
                    results[category][tool_name] = version
                except Exception as e:
                    results[category][tool_name] = f"Error: {str(e)[:30]}"

        return results
    
    def export_to_json(self, results: Dict[str, Dict[str, str]], filename: str = "versions.json"):
        """Export results to JSON file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            return True, f"Exported to {filename}"
        except Exception as e:
            return False, f"Export failed: {str(e)}"
    
    def export_to_text(self, results: Dict[str, Dict[str, str]], filename: str = "versions.txt"):
        """Export results to text file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("Programming Tools Version Report\n")
                f.write("=" * 40 + "\n\n")
                
                for category, tools in results.items():
                    f.write(f"{category}:\n")
                    f.write("-" * len(category) + "\n")
                    for tool, version in tools.items():
                        f.write(f"  {tool}: {version}\n")
                    f.write("\n")
            
            return True, f"Exported to {filename}"
        except Exception as e:
            return False, f"Export failed: {str(e)}"
