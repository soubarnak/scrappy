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
echo  [1/5] Installing core Python packages...
pip install -r requirements.txt --quiet --upgrade
if errorlevel 1 ( echo  [ERROR] pip install failed. & pause & exit /b 1 )

:: ── pywebview (native desktop window via Edge WebView2 — no .NET needed) ──────
echo  [2/5] Installing pywebview + comtypes (native window)...
pip install pywebview comtypes --quiet
if errorlevel 1 (
    echo  [INFO] pywebview skipped — app will open in your default browser instead.
) else (
    echo  [OK] pywebview installed — app will open as a native desktop window.
)

echo  [3/5] Installing Playwright Chromium...
python -m playwright install chromium
if errorlevel 1 ( echo  [WARNING] Chromium install may have failed — try manually later. )

echo  [4/5] Installing frontend npm packages...
cd frontend
call npm install --silent
if errorlevel 1 ( echo  [ERROR] npm install failed. & cd .. & pause & exit /b 1 )

echo  [5/5] Building React UI (shadcn/ui + Cosmic Night theme)...
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
