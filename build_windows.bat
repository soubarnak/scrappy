@echo off
:: Google Maps Scraper — Windows Build Script
:: Produces: dist\GoogleMapsScraper.exe  +  installer_output\*_Setup.exe
::
:: Author    : Soubarna Karmakar
:: Copyright : (c) 2025 Soubarna Karmakar. All rights reserved.
setlocal EnableDelayedExpansion
title Google Maps Scraper — Windows Build
color 0B
cd /d "%~dp0"

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║   Google Maps Scraper v2.0 — Windows Build          ║
echo  ║   Author: Soubarna Karmakar                         ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

:: ── Pre-flight checks ────────────────────────────────────────────────────────
python --version >nul 2>&1 || ( echo [ERROR] Python not found. & goto :fail )
node   --version >nul 2>&1 || ( echo [ERROR] Node.js not found. & goto :fail )
echo  [OK] Python & python --version
echo  [OK] Node   & node --version

:: ── Step 1: Python deps ──────────────────────────────────────────────────────
echo.
echo  [1/5] Installing Python dependencies...
pip install -r requirements.txt --quiet --upgrade
pip install pyinstaller --quiet --upgrade
if errorlevel 1 ( echo [ERROR] pip failed. & goto :fail )

:: ── Step 2: Build React frontend ─────────────────────────────────────────────
echo  [2/5] Building React frontend (shadcn/ui)...
cd frontend
call npm install --silent
call npm run build --silent
if errorlevel 1 ( echo [ERROR] npm build failed. & cd .. & goto :fail )
cd ..

:: ── Step 3: Playwright Chromium ──────────────────────────────────────────────
echo  [3/5] Installing Playwright Chromium...
python -m playwright install chromium

:: ── Step 4: PyInstaller (bundles Python + app + React build) ─────────────────
echo  [4/5] Building standalone executable with PyInstaller...
echo        (This may take 3-5 minutes — please wait)
pyinstaller app.spec --clean --noconfirm
if errorlevel 1 ( echo [ERROR] PyInstaller failed. & goto :fail )

echo.
echo  ════════════════════════════════════════════════════════
echo   Executable ready:  dist\GoogleMapsScraper\GoogleMapsScraper.exe
echo  ════════════════════════════════════════════════════════

:: ── Step 5: Inno Setup installer ─────────────────────────────────────────────
echo.
echo  [5/5] Checking for Inno Setup 6...
set "ISCC="
for %%P in (
    "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
    "%ProgramFiles%\Inno Setup 6\ISCC.exe"
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) do ( if exist "%%~P" ( set "ISCC=%%~P" & goto :found_iscc ) )
goto :no_iscc

:found_iscc
echo  [OK] Inno Setup found — building installer...
mkdir installer_output 2>nul
"%ISCC%" installer.iss
if errorlevel 1 (
    echo  [WARNING] Inno Setup build failed — exe still usable from dist\
) else (
    echo.
    echo  ════════════════════════════════════════════════════════
    echo   Installer ready:  installer_output\GoogleMapsScraper_Setup.exe
    echo   Upload this file to GitHub Releases for users to download!
    echo  ════════════════════════════════════════════════════════
)
goto :done

:no_iscc
echo  [INFO] Inno Setup 6 not found.
echo         Download: https://jrsoftware.org/isdl.php
echo         Then re-run this script to generate the installer .exe

:done
echo.
pause
exit /b 0

:fail
echo.
echo  ════════════════════════════════════════════════════════
echo   Build FAILED — check errors above.
echo  ════════════════════════════════════════════════════════
pause
exit /b 1
