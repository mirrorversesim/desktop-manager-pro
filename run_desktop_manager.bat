@echo off
REM Desktop Manager Launcher
REM This script can be run from anywhere to launch the desktop manager

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"

REM Change to the script directory
cd /d "%SCRIPT_DIR%"

REM Launch the desktop manager
echo Starting Desktop Window & Process Manager...
echo Running from: %SCRIPT_DIR%
echo.
python main.py

REM If there was an error, pause so user can see it
if errorlevel 1 (
    echo.
    echo Application exited with an error.
    pause
) 