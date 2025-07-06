@echo off
echo Desktop Window & Process Manager - Installation Script
echo =====================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

echo Python found. Installing dependencies...
echo.

REM Install requirements
echo Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Dependencies installed successfully.
echo.

REM Try to run pywin32 post-install
echo Running pywin32 post-install script...
python -m pywin32_postinstall -install
if errorlevel 1 (
    echo WARNING: pywin32 post-install failed. You may need to run as Administrator.
    echo.
)

echo.
echo Installation completed!
echo.
echo To test the installation, run:
echo   python test_installation.py
echo.
echo To start the application, run:
echo   python main.py
echo.
pause 