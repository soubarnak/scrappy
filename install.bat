@echo off
:: Google Maps Scraper — One-click Dev Setup
:: Author    : Soubarna Karmakar
:: Copyright : (c) 2025 Soubarna Karmakar. All rights reserved.
setlocal EnableDelayedExpansion
title Google Maps Scraper — Setup
color 0B

echo.
echo  =====================================================
echo   Google Maps Scraper v2.0 — Setup
echo   by Soubarna Karmakar
echo  =====================================================
echo.

:: ── Python ──────────────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found. Install Python 3.10+ from https://python.org
    pause & exit /b 1
)
echo  [OK] & python --version

:: ── Node.js ─────────────────────────────────────────────────────────────────
node --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Node.js not found. Install Node.js 18+ from https://nodejs.org
    pause & exit /b 1
)
echo  [OK] Node & node --version

echo.
echo  [1/4] Installing Python packages...
pip install -r requirements.txt --quiet --upgrade
if errorlevel 1 ( echo  [ERROR] pip install failed. & pause & exit /b 1 )

echo  [2/4] Installing Playwright Chromium...
python -m playwright install chromium
if errorlevel 1 ( echo  [WARNING] Chromium install may have failed — try manually later. )

echo  [3/4] Installing frontend npm packages...
cd frontend
call npm install --silent
if errorlevel 1 ( echo  [ERROR] npm install failed. & cd .. & pause & exit /b 1 )

echo  [4/4] Building React UI (shadcn/ui + Cosmic Night theme)...
call npm run build --silent
if errorlevel 1 ( echo  [ERROR] npm build failed. & cd .. & pause & exit /b 1 )
cd ..

echo.
echo  =====================================================
echo   Setup complete!
echo   Run the app:  run.bat
echo  =====================================================
echo.
pause
