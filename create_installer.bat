@echo off
echo ========================================
echo Desktop Manager Installer Builder
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or later
    pause
    exit /b 1
)

echo Building Desktop Manager installer...
echo.

REM Run the build script
python build_installer.py

if errorlevel 1 (
    echo.
    echo Build failed! Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Files created:
echo - dist\DesktopManager.exe (standalone executable)
echo - installer.nsi (NSIS installer script)
echo - LICENSE.txt (license file)
echo - README.txt (readme file)
echo.

REM Check if NSIS is available
makensis -VERSION >nul 2>&1
if errorlevel 1 (
    echo NSIS is not installed or not in PATH
    echo.
    echo To create the installer:
    echo 1. Download and install NSIS from: https://nsis.sourceforge.io/
    echo 2. Add NSIS to your PATH or run from NSIS installation directory
    echo 3. Run: makensis installer.nsi
    echo.
    echo The installer will be created as: DesktopManager-Setup.exe
) else (
    echo Creating installer with NSIS...
    makensis installer.nsi
    if errorlevel 1 (
        echo.
        echo Installer creation failed!
    ) else (
        echo.
        echo ========================================
        echo Installer created successfully!
        echo ========================================
        echo.
        echo Installer file: DesktopManager-Setup.exe
        echo.
        echo You can now distribute this installer file.
    )
)

echo.
pause 