# Windows Service Manager - PowerShell Admin Launcher
# This script ensures the application runs with administrator privileges

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Windows Service Manager" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This application requires administrator privileges for:" -ForegroundColor Yellow
Write-Host "- Windows service management" -ForegroundColor White
Write-Host "- System cleanup operations" -ForegroundColor White
Write-Host "- Windows Update control" -ForegroundColor White
Write-Host "- Hyper-V management" -ForegroundColor White
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if ($isAdmin) {
    Write-Host "Running with administrator privileges..." -ForegroundColor Green
    Write-Host "Starting application..." -ForegroundColor Green
    Write-Host ""
    
    # Run the Python application
    python main.py
} else {
    Write-Host "Requesting administrator privileges..." -ForegroundColor Yellow
    Write-Host "Please click 'Yes' in the User Account Control dialog." -ForegroundColor Yellow
    Write-Host ""
    
    # Restart with administrator privileges
    try {
        Start-Process python -ArgumentList "main.py" -Verb RunAs
        Write-Host "Administrator request sent. Check for UAC dialog." -ForegroundColor Green
    } catch {
        Write-Host "Failed to request administrator privileges: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Please manually run the application as Administrator." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
