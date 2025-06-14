@echo off

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.6+ and add it to your PATH
    pause
    exit /b 1
)

REM Create a temporary VBS script to run the application without showing a window
echo Set WshShell = CreateObject("WScript.Shell") > %temp%\runhidden.vbs
echo WshShell.Run "pythonw ""%~dp0main.py""", 0, false >> %temp%\runhidden.vbs

REM Run the VBS script to launch the application without a window
start /wait wscript %temp%\runhidden.vbs

REM Clean up the temporary VBS script
del %temp%\runhidden.vbs
