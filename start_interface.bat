@echo off
echo Biocat Database Interface Launcher
echo ===================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

echo Python found. Starting interface...
echo.

REM Try to launch using the Python launcher
python launch.py

REM If that fails, try direct app launch
if errorlevel 1 (
    echo.
    echo Launch script failed, trying direct app launch...
    python app.py
)

echo.
echo Interface has stopped.
pause
