@echo off
REM Windows Service Manager - Run as Administrator
REM This batch file ensures the application runs with administrator privileges

echo ========================================
echo Windows Service Manager
echo ========================================
echo.
echo This application requires administrator privileges for:
echo - Windows service management
echo - System cleanup operations  
echo - Windows Update control
echo - Hyper-V management
echo.

REM Check if already running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges...
    echo Starting application...
    echo.
    python main.py
) else (
    echo Requesting administrator privileges...
    echo Please click "Yes" in the User Account Control dialog.
    echo.
    powershell -Command "Start-Process python -ArgumentList 'main.py' -Verb RunAs"
)

pause
