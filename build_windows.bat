@echo off
:: Author: Soubarna Karmakar — Copyright (c) 2025. All rights reserved.
setlocal EnableDelayedExpansion
title Google Maps Scraper — Windows Build
color 0B

echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║   Google Maps Scraper — Windows Build Tool       ║
echo  ║   Produces:  dist\GoogleMapsScraper\             ║
echo  ║              installer_output\*_Setup.exe        ║
echo  ╚══════════════════════════════════════════════════╝
echo.

:: ── Change to the folder containing this script ──────────────────────────────
cd /d "%~dp0"

:: ── 1. Verify Python ─────────────────────────────────────────────────────────
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python not found in PATH.
    echo         Download Python 3.10+ from https://python.org
    goto :fail
)
echo  [OK] Python: & python --version

:: ── 2. Install / upgrade required packages ───────────────────────────────────
echo.
echo  [STEP 1/4] Installing Python dependencies...
pip install -r requirements.txt --quiet --upgrade
if %errorlevel% neq 0 ( echo  [ERROR] pip install failed. & goto :fail )

echo  [STEP 2/4] Installing PyInstaller...
pip install pyinstaller --quiet --upgrade
if %errorlevel% neq 0 ( echo  [ERROR] PyInstaller install failed. & goto :fail )
echo  [OK] PyInstaller: & pyinstaller --version

:: ── 3. Install Playwright Chromium (needed so collect_all works) ─────────────
echo.
echo  [STEP 3/4] Ensuring Playwright Chromium is present...
python -m playwright install chromium
if %errorlevel% neq 0 (
    echo  [WARNING] Playwright browser install failed — continuing anyway.
)

:: ── 4. Build with PyInstaller ─────────────────────────────────────────────────
echo.
echo  [STEP 4/4] Building executable with PyInstaller...
echo             (This may take several minutes)
echo.
pyinstaller scraper.spec --clean --noconfirm
if %errorlevel% neq 0 ( echo  [ERROR] PyInstaller build failed. & goto :fail )

echo.
echo  ════════════════════════════════════════════════════
echo   Build successful!
echo   Executable folder:  dist\GoogleMapsScraper\
echo   Launch directly:    dist\GoogleMapsScraper\GoogleMapsScraper.exe
echo  ════════════════════════════════════════════════════

:: ── 5. Optional: create installer with Inno Setup ────────────────────────────
echo.
echo  Checking for Inno Setup 6...

set "ISCC="
for %%P in (
    "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
    "%ProgramFiles%\Inno Setup 6\ISCC.exe"
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) do (
    if exist "%%~P" ( set "ISCC=%%~P" & goto :found_iscc )
)
goto :no_iscc

:found_iscc
echo  [OK] Inno Setup found: %ISCC%
echo  Building installer package...
mkdir installer_output 2>nul
"%ISCC%" installer.iss
if %errorlevel% neq 0 (
    echo  [WARNING] Inno Setup build failed.
) else (
    echo.
    echo  ════════════════════════════════════════════════════
    echo   Installer ready:  installer_output\*_Setup.exe
    echo  ════════════════════════════════════════════════════
)
goto :done

:no_iscc
echo  [INFO] Inno Setup 6 not found — skipping installer creation.
echo         To create a Windows installer:
echo           1. Download Inno Setup 6 from https://jrsoftware.org/isdl.php
echo           2. Re-run this script  (OR run: ISCC installer.iss)
goto :done

:fail
echo.
echo  [FAILED] Build did not complete. Check errors above.
pause
exit /b 1

:done
echo.
pause
