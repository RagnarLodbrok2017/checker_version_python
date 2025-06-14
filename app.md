# Programming Tools Version Checker - Complete Application Documentation

## Application Overview

The Programming Tools Version Checker is a comprehensive desktop application designed to detect, manage, and install development tools on Windows systems. It provides a unified interface for checking versions of programming languages, package managers, frameworks, development tools, and includes advanced browser backup and restore functionality.

## Core Purpose and Functionality

### Primary Functions
1. **Version Detection**: Automatically detects and displays versions of 35+ programming tools and languages
2. **Automatic Installation**: One-click installation of missing tools using package managers (winget, chocolatey, npm)
3. **Browser Data Management**: Complete backup and restore functionality for major browsers
4. **System Management**: PC cleanup tools and installed program management
5. **Data Export**: Export results to JSON/text formats and bookmarks to HTML

### Target Users
- Software developers and programmers
- System administrators
- IT professionals managing development environments
- Users migrating between computers or browsers

## Application Architecture

### Main Components
1. **main.py**: Application entry point with login system
2. **login.py**: Authentication window with dark theme UI
3. **gui.py**: Main GUI interface using tkinter (3176 lines)
4. **version_checker.py**: Core version checking and installation logic (808 lines)
5. **browser_backup.py**: Browser data backup and restore functionality (567 lines)

### Authentication System
- **Login Window**: Dark-themed login interface
- **Default Credentials**: Username: "Elnakieb", Password: "Elnakieb"
- **Security**: Basic authentication (suitable for personal/development use)

## Detailed Feature Documentation

### 1. Version Checking System

#### Supported Tool Categories

**Languages (8 tools)**:
- Python, Node.js, PHP, Java, Go, Rust, Ruby, C# (dotnet)

**Package Managers (9 tools)**:
- npm, pip, Composer, Yarn, pnpm, Cargo, gem, Maven, Gradle

**Frontend Tools (5 tools)**:
- Vue CLI, Angular CLI, Vite, Webpack, TypeScript

**Version Control (2 tools)**:
- Git, SVN

**Databases (4 tools)**:
- MySQL, PostgreSQL, MongoDB, SQLite

**Development Tools (6 tools)**:
- Docker, Docker Compose, VS Code, Cursor, Windsurf, Postman

**Development Environments (2 tools)**:
- WAMP Server, XAMPP

**Cloud Tools (4 tools)**:
- AWS CLI, Azure CLI, Google Cloud SDK, Heroku CLI

#### Enhanced Detection Features
- **Alternative Path Detection**: Searches common installation directories
- **Service Detection**: Checks Windows services for server applications
- **Registry Scanning**: Uses PowerShell to query Windows registry
- **Glob Pattern Matching**: Finds tools in various installation paths
- **Version Extraction**: Intelligent parsing of version strings

### 2. Installation System

#### Supported Package Managers
- **winget**: Windows Package Manager (preferred)
- **chocolatey**: Community package manager
- **npm**: Node.js package manager for frontend tools

#### Installable Tools (15+ tools)
- Languages: Python, Node.js, Go, Rust
- Development Tools: Git, Docker
- Frontend Tools: Vue CLI, Angular CLI, TypeScript, Yarn, pnpm

#### Installation Process
1. **Detection**: Check available package managers
2. **Selection**: User selects tools to install
3. **Confirmation**: Display installation details
4. **Execution**: Run installation commands in background
5. **Verification**: Re-check versions after installation

### 3. Browser Backup and Restore System

#### Supported Browsers
- **Google Chrome**: Full profile backup
- **Brave Browser**: Privacy-focused browser data
- **Microsoft Edge**: Microsoft's Chromium-based browser
- **Mozilla Firefox**: Complete Firefox profile data

#### Backup Data Types
- **Bookmarks**: All saved bookmarks and folders
- **History**: Complete browsing history with timestamps
- **Login Data**: Saved passwords (encrypted)
- **Preferences**: Browser settings and configurations
- **Cookies**: Website cookies and session data
- **Extensions**: Installed extensions and their settings
- **Local Storage**: Website offline data
- **Session Storage**: Temporary session data

#### Backup Features
- **Multi-Profile Support**: Backup multiple browser profiles
- **Cross-Browser Migration**: Restore data between different browsers
- **Timestamped Backups**: Automatic timestamp naming
- **Backup Management**: View, delete, and organize backups
- **Progress Tracking**: Real-time backup/restore progress
- **HTML Export**: Export bookmarks to standard HTML format

### 4. System Management Tools

#### Installed Programs Manager
- **Program Detection**: Scans Windows registry for installed programs
- **Search Functionality**: Filter programs by name, publisher, or version
- **Uninstallation**: Direct uninstall capability with confirmation
- **Registry Cleanup**: Detect and remove leftover registry entries
- **Progress Tracking**: Real-time uninstallation progress

#### PC Cleanup Tools
- **Temporary Files**: Clean user and system temp files
- **Prefetch Files**: Clean Windows prefetch directory
- **Registry Cleanup**: Remove invalid registry entries
- **Browser Cache**: Clean browser cache files
- **Recycle Bin**: Empty recycle bin
- **System Logs**: Clean Windows log files

### 5. User Interface Design

#### Main Window Layout
- **Full Screen**: Opens maximized for optimal viewing
- **Tree View**: Hierarchical display of tools by category
- **Status Bar**: Real-time operation status
- **Progress Bar**: Visual progress indication
- **Control Panel**: Action buttons and export options

#### Color Coding System
- **Green**: Tool installed and version detected
- **Red**: Tool not installed or not found
- **Blue**: Installable tools with install buttons
- **Gray**: Tools being processed

#### Menu System
- **File Menu**: Export/Import functionality, Exit
- **Tools Menu**: Version checking, Auto-install, System management
- **Browser Backup Menu**: Backup, Restore, Manage, Export bookmarks
- **Help Menu**: About dialog

### 6. Data Export and Import

#### Export Formats
- **JSON**: Structured data with full details
- **Text**: Human-readable format
- **HTML**: Bookmarks in standard format

#### Export Features
- **Timestamped Files**: Automatic timestamp in filenames
- **Complete Data**: All detected versions and status
- **Backup Integration**: Export backup information
- **Cross-Platform**: Standard formats for portability

## User Workflow and Navigation

### Initial Setup
1. **Launch Application**: Run main.py
2. **Login**: Enter credentials (Elnakieb/Elnakieb)
3. **Main Interface**: Full-screen application window opens

### Version Checking Workflow
1. **Start Check**: Click "Check Versions" button or use Tools menu
2. **Progress Monitoring**: Watch progress bar and status updates
3. **Review Results**: Examine tree view with color-coded results
4. **Install Missing Tools**: Double-click installable tools or use install buttons
5. **Export Results**: Save results using File menu options

### Browser Backup Workflow
1. **Access Menu**: Browser Backup → Backup Browser Data
2. **Select Browser**: Choose browser and profiles to backup
3. **Monitor Progress**: Watch backup progress dialog
4. **Manage Backups**: Use Backup Manager to view/delete backups
5. **Restore Data**: Use restore dialog to recover data

### System Management Workflow
1. **View Programs**: Tools → Installed Programs
2. **Search/Filter**: Use search box to find specific programs
3. **Uninstall**: Double-click program to uninstall
4. **Cleanup System**: Tools → PC Cleanup for system maintenance

## Configuration and Customization

### Adding New Tools
Tools can be added by modifying the `tools` dictionary in `version_checker.py`:
```python
'Category Name': {
    'Tool Name': ['command', '--version'],
}
```

### Installation Commands
New installable tools can be added to the `installable_tools` dictionary:
```python
'Tool Name': {
    'winget': ['winget', 'install', 'package.id'],
    'chocolatey': ['choco', 'install', 'package', '-y'],
    'description': 'Tool description'
}
```

### Theme Customization
Colors and styling can be modified in the `colors` dictionary in both `gui.py` and `login.py`.

## Technical Implementation Details

### Threading Model
- **Background Processing**: Version checking runs in separate threads
- **UI Responsiveness**: Main UI thread remains responsive during operations
- **Progress Updates**: Thread-safe progress reporting to UI

### Error Handling
- **Timeout Protection**: 5-second timeout for version commands
- **Permission Handling**: Graceful handling of permission errors
- **File Locking**: Handles browser files that may be in use
- **Registry Access**: Safe registry operations with error recovery

### Cross-Platform Considerations
- **Windows Focus**: Optimized for Windows with PowerShell integration
- **Path Detection**: Multiple path checking for different OS layouts
- **Command Adaptation**: Different commands for different platforms

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10 or later (primary), macOS, Linux (limited)
- **Python**: 3.6 or higher
- **Memory**: 50MB RAM minimum
- **Storage**: 10MB for application, additional space for backups
- **Dependencies**: Python standard library only (no pip installs required)

### Recommended Requirements
- **Operating System**: Windows 11
- **Python**: 3.9 or later
- **Memory**: 100MB RAM for optimal performance
- **Storage**: 1GB for browser backups
- **Permissions**: Administrator rights for system management features

## Security Considerations

### Authentication
- **Basic Security**: Simple username/password authentication
- **Local Access**: Designed for single-user systems
- **No Network**: No network authentication or remote access

### Data Protection
- **Local Storage**: All data stored locally
- **Encrypted Passwords**: Browser passwords remain encrypted
- **Backup Security**: Backups stored in local directory
- **Registry Safety**: Safe registry operations with error handling

## Troubleshooting Guide

### Common Issues
1. **Tools Not Detected**: Check PATH environment variable
2. **Installation Failures**: Verify package manager availability
3. **Browser Backup Errors**: Close browser before backup
4. **Permission Errors**: Run as administrator if needed
5. **GUI Issues**: Ensure tkinter is properly installed

### Performance Optimization
- **Selective Checking**: Check only needed tool categories
- **Background Processing**: Use threading for long operations
- **Cleanup**: Regular cleanup of temporary files and old backups

This comprehensive documentation covers all aspects of the Programming Tools Version Checker application, providing complete information about its functionality, features, and usage patterns.
