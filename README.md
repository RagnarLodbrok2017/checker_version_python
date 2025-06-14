# Programming Tools Version Checker

A comprehensive desktop application that displays versions of programming languages, package managers, frameworks, and development tools installed on your Windows system.

## Features

- **Comprehensive Tool Detection**: Checks versions of 35+ programming tools, languages, and development environments
- **Automatic Installation**: One-click installation for missing tools via winget, npm, or chocolatey
- **Browser Backup & Restore**: Complete backup and restore of browser data (bookmarks, history, passwords, etc.)
- **Categorized Display**: Organizes tools into logical categories (Languages, Package Managers, etc.)
- **User-Friendly GUI**: Clean tkinter-based interface with tree view and install buttons
- **Export Functionality**: Save results to JSON or text files and export bookmarks to HTML
- **Real-time Status**: Progress indication and status updates
- **Cross-platform**: Works on Windows, macOS, and Linux

## Supported Tools

### Languages
- Python
- Node.js
- PHP
- Java
- Go
- Rust
- Ruby
- C# (dotnet)

### Package Managers
- npm
- pip
- Composer
- Yarn
- pnpm
- Cargo
- gem
- Maven
- Gradle

### Frontend Tools
- Vue CLI
- Angular CLI
- Create React App
- Vite
- Webpack

### Version Control
- Git
- SVN

### Databases
- MySQL
- PostgreSQL
- MongoDB
- SQLite

### Development Tools
- Docker
- Docker Compose
- VS Code
- Cursor
- Windsurf
- Postman

### Development Environments
- WAMP Server
- XAMPP

### Browser Backup & Restore
- Google Chrome
- Brave Browser
- Microsoft Edge
- Mozilla Firefox
- Cross-browser data migration

### Cloud Tools
- AWS CLI
- Azure CLI
- Google Cloud SDK
- Heroku CLI

## Installation

1. **Clone or download** this repository
2. **Ensure Python 3.6+** is installed on your system
3. **No additional packages required** - uses only Python standard library

```bash
# Clone the repository
git clone <repository-url>
cd programming-tools-version-checker

# Run the application
python main.py
```

## Usage

1. **Launch the application**:
   ```bash
   python main.py
   ```

2. **Check versions**:
   - Click the "Check Versions" button
   - Wait for the scan to complete (may take 30-60 seconds)
   - View results in the tree view

3. **Install missing tools**:
   - Look for tools marked "📦 Install" in the Action column
   - Double-click any installable tool OR select it and click "Install Selected Tool"
   - Confirm installation when prompted
   - Wait for installation to complete (automatic refresh follows)

4. **Browser backup and restore**:
   - Go to "Browser Backup" menu
   - Select "Backup Browser Data" to create backups
   - Use "Restore Browser Data" to restore from backups
   - "Manage Backups" to view and delete old backups
   - "Export Bookmarks to HTML" for bookmark portability

5. **Export results**:
   - Click "Export to JSON" or "Export to Text"
   - Choose save location
   - Results will be saved with timestamp

## GUI Interface

- **Left Panel**: Control buttons and export options
- **Right Panel**: Tree view showing categorized results
- **Status Bar**: Current operation status
- **Progress Bar**: Visual indication of scanning progress

## Color Coding

- **Green**: Tool is installed and version detected
- **Red**: Tool is not installed or not found in PATH

## File Structure

```
programming-tools-version-checker/
├── main.py              # Application entry point
├── gui.py               # GUI interface using tkinter
├── version_checker.py   # Core version checking logic
├── requirements.txt     # Python dependencies (minimal)
└── README.md           # This file
```

## How It Works

1. **Command Execution**: Uses subprocess to run version commands
2. **Enhanced Detection**: Alternative detection methods for tools not in PATH
3. **Development Environments**: Specialized detection for WAMP and XAMPP installations
4. **Error Handling**: Gracefully handles missing tools and timeouts
5. **Threading**: Version checking runs in background to keep GUI responsive
6. **Cross-platform**: Adapts commands for different operating systems

## Enhanced Detection Features

### WAMP Server Detection
- Searches common installation paths (C:\wamp64, C:\wamp, etc.)
- Extracts version from wampmanager.exe and configuration files
- Detects Apache versions as indicators
- Checks for WAMP services

### XAMPP Detection
- Searches common installation paths (C:\xampp, etc.)
- Extracts version from xampp-control.exe and readme files
- Detects Apache versions as indicators
- Checks for XAMPP services

### MySQL Enhanced Detection
- Searches WAMP, XAMPP, and standalone MySQL installations
- Uses glob patterns to find different MySQL versions
- Checks multiple installation directories

## Browser Backup & Restore Features

### Supported Browsers
- **Google Chrome**: Full profile backup including bookmarks, history, passwords
- **Brave Browser**: Complete data backup with privacy settings
- **Microsoft Edge**: All user data and preferences
- **Mozilla Firefox**: Bookmarks, history, passwords, and add-ons

### Backup Data Types
- **Bookmarks and Favorites**: All saved bookmarks and bookmark folders
- **Browsing History**: Complete browsing history with timestamps
- **Saved Passwords**: Encrypted password storage (browser's native encryption)
- **Cookies and Session Data**: Login sessions and website preferences
- **Extensions and Add-ons**: Installed browser extensions and their settings
- **Browser Preferences**: All browser settings and configurations
- **Local Storage**: Website data and offline storage
- **Form History**: Saved form data and autofill information

### Backup Features
- **Multi-Browser Support**: Backup multiple browsers simultaneously
- **Profile Detection**: Automatically detects all browser profiles
- **Incremental Backups**: Create multiple backups with timestamps
- **Cross-Browser Restore**: Restore data from one browser to another
- **Backup Management**: View, delete, and organize backups
- **HTML Export**: Export bookmarks to standard HTML format
- **Progress Tracking**: Real-time backup and restore progress
- **Error Handling**: Graceful handling of locked files and permissions

### Use Cases
- **Windows Reinstallation**: Backup before OS reinstall, restore after
- **Computer Migration**: Move browser data to new computer
- **Browser Switching**: Migrate from one browser to another
- **Data Protection**: Regular backups to prevent data loss
- **Profile Synchronization**: Share browser data between computers

## Customization

You can easily add more tools by editing the `tools` dictionary in `version_checker.py`:

```python
'New Category': {
    'Tool Name': ['command', '--version'],
}
```

## Troubleshooting

### Common Issues

1. **"Not installed" for installed tools**:
   - Tool may not be in system PATH
   - Try running the version command manually in terminal

2. **GUI doesn't start**:
   - Ensure tkinter is installed (usually comes with Python)
   - On Linux: `sudo apt-get install python3-tk`

3. **Slow scanning**:
   - Some tools may take time to respond
   - Network-dependent tools (like cloud CLIs) may timeout

### Windows-Specific Notes

- Some tools may require full path specification
- PowerShell vs Command Prompt differences handled automatically
- Administrator privileges may be needed for some system tools

## Contributing

Feel free to contribute by:
- Adding support for more tools
- Improving the GUI interface
- Adding new export formats
- Fixing bugs or improving error handling

## License

This project is open source and available under the MIT License.

## System Requirements

- **Python**: 3.6 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimal (< 50MB)
- **Dependencies**: Python standard library only
