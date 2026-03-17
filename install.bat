@echo off
title Google Maps Scraper — Installer
color 0B
echo.
echo  ============================================
echo   Google Maps Scraper — Setup
echo  ============================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python is not installed or not in PATH.
    echo  Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

echo  [OK] Python found:
python --version
echo.

:: Install pip packages
echo  Installing Python packages...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo  [ERROR] pip install failed. Check your internet connection.
    pause
    exit /b 1
)
echo  [OK] Python packages installed.
echo.

:: Install Playwright Chromium browser
echo  Installing Playwright Chromium browser...
python -m playwright install chromium
if %errorlevel% neq 0 (
    echo  [WARNING] Playwright browser install may have failed.
    echo  Try running manually:  python -m playwright install chromium
) else (
    echo  [OK] Playwright Chromium ready.
)

echo.
echo  ============================================
echo   Setup complete!  Run:  run.bat
echo  ============================================
echo.
pause
