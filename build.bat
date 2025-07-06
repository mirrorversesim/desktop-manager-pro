@echo off
echo Building Desktop Manager Pro...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python and try again.
    pause
    exit /b 1
)

REM Run the build script
python build_exe.py

echo.
echo Build process completed!
pause 