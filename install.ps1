# Desktop Window & Process Manager - Installation Script (PowerShell)
# =================================================================

Write-Host "Desktop Window & Process Manager - Installation Script" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Green
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8 or higher from https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Installing Python dependencies..." -ForegroundColor Cyan

# Install requirements
try {
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        throw "pip install failed with exit code $LASTEXITCODE"
    }
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "✗ ERROR: Failed to install dependencies" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Try to run pywin32 post-install
Write-Host "Running pywin32 post-install script..." -ForegroundColor Cyan
try {
    python -m pywin32_postinstall -install
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ pywin32 post-install completed successfully" -ForegroundColor Green
    } else {
        Write-Host "⚠ WARNING: pywin32 post-install failed. You may need to run as Administrator." -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ WARNING: pywin32 post-install failed. You may need to run as Administrator." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Installation completed!" -ForegroundColor Green
Write-Host ""

# Test the installation
Write-Host "Testing installation..." -ForegroundColor Cyan
try {
    python test_installation.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Installation test passed!" -ForegroundColor Green
    } else {
        Write-Host "⚠ Installation test failed. Check the output above." -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ Could not run installation test: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. To test the installation: python test_installation.py" -ForegroundColor White
Write-Host "2. To start the application: python main.py" -ForegroundColor White
Write-Host "3. To stop the application: Press Ctrl+C" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit" 