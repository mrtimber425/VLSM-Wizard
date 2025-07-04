@echo off
setlocal enabledelayedexpansion

echo 🔧 Checking for Python...
where python >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.7+ and add it to PATH.
    pause
    exit /b
)

echo 🔧 Creating virtual environment...
if not exist venv (
    python -m venv venv
)

echo ✅ Activating environment...
call venv\Scripts\activate.bat

echo 📦 Installing dependencies...
pip install --upgrade pip >nul 2>&1
pip install pyqt5 numpy >nul 2>&1

echo 🚀 Launching Subnet Calculator...

if not exist vlsmwiz.py (
    echo ❌ Error: subnet_calculator.py not found in this folder.
    echo Make sure this launcher is placed in the same directory.
    pause
    exit /b
)

python vlsmwiz.py

echo ✅ Done.
pause
