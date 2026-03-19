@echo off
:: Scrappy — Windows Build Script
:: Produces a fully self-contained installer:
::   installer_output\Scrappy_Setup_v2.0.exe
::
:: What gets bundled:
::   - Python runtime (no Python needed on end-user machine)
::   - All Python packages (FastAPI, Playwright lib, openpyxl, etc.)
::   - React frontend (pre-built static files)
::   - Playwright Chromium browser (~130 MB, copied into dist\)
::   - Microsoft Edge WebView2 bootstrapper (for native window)
::
:: Requirements on THIS machine (developer):
::   - Python 3.x    https://python.org
::   - Node.js 18+   https://nodejs.org
::   - Inno Setup 6  https://jrsoftware.org/isdl.php  (for the installer step)
::
:: Author    : Soubarna Karmakar
:: Copyright : (c) 2025 Soubarna Karmakar. All rights reserved.
setlocal EnableDelayedExpansion
title Scrappy — Windows Build
color 0B
cd /d "%~dp0"

echo.
echo  ============================================================
echo   Scrappy v2.0 — Windows Build
echo   Author: Soubarna Karmakar
echo   Output: installer_output\Scrappy_Setup_v2.0.exe
echo  ============================================================
echo.

:: ── Pre-flight checks ─────────────────────────────────────────────────────────
python --version >nul 2>&1 || ( echo [ERROR] Python not found. Install from https://python.org & goto :fail )
node   --version >nul 2>&1 || ( echo [ERROR] Node.js not found. Install from https://nodejs.org  & goto :fail )
echo  [OK] Python  & python --version
echo  [OK] Node.js & node --version

:: ── Step 1: Python packages ───────────────────────────────────────────────────
echo.
echo  [1/6] Installing Python dependencies...
pip install -r requirements.txt --quiet --upgrade
if errorlevel 1 ( echo [ERROR] pip install failed. & goto :fail )

echo  [1b] Installing pywebview + comtypes (native window via Edge WebView2)...
pip install pywebview comtypes --quiet 2>nul || echo  [INFO] pywebview optional — skipping.

echo  [1c] Installing PyInstaller...
pip install pyinstaller --quiet --upgrade
if errorlevel 1 ( echo [ERROR] PyInstaller install failed. & goto :fail )

:: ── Step 2: Build React frontend ──────────────────────────────────────────────
echo.
echo  [2/6] Building React frontend...
cd frontend
call npm install --silent
if errorlevel 1 ( echo [ERROR] npm install failed. & cd .. & goto :fail )
call npm run build --silent
if errorlevel 1 ( echo [ERROR] npm build failed.    & cd .. & goto :fail )
cd ..
echo  [OK] React build complete — frontend\dist\

:: ── Step 3: Install Playwright Chromium ───────────────────────────────────────
echo.
echo  [3/6] Installing Playwright Chromium browser...
python -m playwright install chromium
if errorlevel 1 ( echo [WARNING] Chromium install may have failed. Continuing... )

:: ── Step 4: PyInstaller — bundle Python + app + React into dist\ ──────────────
echo.
echo  [4/6] Building standalone executable with PyInstaller...
echo        (First run takes 5-10 min — please wait)
pyinstaller app.spec --clean --noconfirm
if errorlevel 1 ( echo [ERROR] PyInstaller failed. & goto :fail )
echo  [OK] PyInstaller complete — dist\Scrappy\

:: ── Step 5: Copy Playwright Chromium into the dist folder ─────────────────────
::
::  Playwright stores Chromium at:
::    %LOCALAPPDATA%\ms-playwright\chromium-{version}\
::  We copy it into dist so end-users don't need to download anything.
::
echo.
echo  [5/6] Bundling Playwright Chromium into dist\...
set "PW_CACHE=%LOCALAPPDATA%\ms-playwright"
set "PW_DEST=dist\Scrappy\_playwright_browsers"
mkdir "%PW_DEST%" 2>nul

set "CHROMIUM_FOUND=0"
for /d %%D in ("%PW_CACHE%\chromium-*") do (
    echo  Copying %%~nxD...
    xcopy "%%D" "%PW_DEST%\%%~nxD\" /E /I /Q /Y >nul
    set "CHROMIUM_FOUND=1"
)

if "!CHROMIUM_FOUND!"=="1" (
    echo  [OK] Playwright Chromium bundled — end-users need NO internet on first launch.
) else (
    echo  [WARNING] Chromium not found at %PW_CACHE%
    echo            Run: python -m playwright install chromium
    echo            Then re-run this script.
    echo            Without bundled Chromium, users need internet on first launch.
)

:: ── Download Microsoft Edge WebView2 Standalone Installer (fully offline) ─────
::
::  We bundle the FULL standalone installer (~170 MB) so end-user machines need
::  NO internet connection during setup.  The installer runs silently and only
::  installs WebView2 if it is not already present (registry check in the .iss).
::
::  Download strategy:
::    1. Query the Microsoft Edge Enterprise API for the latest stable release URL.
::    2. If the API call fails, fall back to the online bootstrapper (~1.5 MB).
::
echo.
echo  [5b] Downloading Microsoft Edge WebView2 Standalone Installer (~170 MB)...
echo       (This is a one-time download — the file is cached in redist\)
mkdir redist 2>nul
if not exist "redist\MicrosoftEdgeWebView2RuntimeInstallerX64.exe" (
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "& { try { " ^
        "  $api = Invoke-RestMethod 'https://edgeupdates.microsoft.com/api/products?view=enterprise'; " ^
        "  $wv2 = $api | Where-Object { $_.Product -eq 'WebView2Runtime' }; " ^
        "  $rel = ($wv2.Releases | Where-Object { $_.Platform -eq 'Windows' -and $_.Architecture -eq 'x64' })[0]; " ^
        "  $art = ($rel.Artifacts | Where-Object { $_.ArtifactName -match 'standalone|exe' })[0]; " ^
        "  if (-not $art) { throw 'Artifact not found' }; " ^
        "  Write-Host ('  Version: ' + $rel.ProductVersion); " ^
        "  Invoke-WebRequest $art.Location -OutFile 'redist\MicrosoftEdgeWebView2RuntimeInstallerX64.exe' -UseBasicParsing; " ^
        "  Write-Host '  [OK] Standalone installer saved.' " ^
        "} catch { " ^
        "  Write-Warning ('API failed: ' + $_); " ^
        "  Write-Host '  Falling back to online bootstrapper...'; " ^
        "  Invoke-WebRequest 'https://go.microsoft.com/fwlink/p/?LinkId=2124703' -OutFile 'redist\MicrosoftEdgeWebView2RuntimeInstallerX64.exe' -UseBasicParsing; " ^
        "  Write-Host '  [OK] Bootstrapper saved (requires internet on target machine).' " ^
        "} }"
    if errorlevel 1 (
        echo  [WARNING] WebView2 download failed. Rebuild and try again.
    )
) else (
    echo  [OK] WebView2 installer already present in redist\ — skipping download.
)

echo.
echo  ============================================================
echo   Executable ready:
echo     dist\Scrappy\Scrappy.exe
echo  ============================================================

:: ── Step 6: Inno Setup installer ──────────────────────────────────────────────
echo.
echo  [6/6] Checking for Inno Setup 6...
set "ISCC="
for %%P in (
    "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
    "%ProgramFiles%\Inno Setup 6\ISCC.exe"
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    "C:\Program Files\Inno Setup 6\ISCC.exe"
) do ( if exist "%%~P" ( set "ISCC=%%~P" & goto :found_iscc ) )
goto :no_iscc

:found_iscc
echo  [OK] Inno Setup found — building installer...
mkdir installer_output 2>nul
"%ISCC%" installer.iss
if errorlevel 1 (
    echo  [WARNING] Inno Setup build failed — exe still usable from dist\
    goto :done
)
echo.
echo  ============================================================
echo   Installer ready:
echo     installer_output\Scrappy_Setup_v2.0.exe
echo.
echo   This single file installs Scrappy on ANY Windows 10/11 PC.
echo   No Python, Node.js, or internet connection required.
echo.
echo   Upload to GitHub Releases for users to download!
echo  ============================================================
goto :done

:no_iscc
echo  [INFO] Inno Setup 6 not found — skipping installer packaging.
echo         Download: https://jrsoftware.org/isdl.php
echo         After installing Inno Setup, re-run this script.
echo         (The exe in dist\ is still usable without the installer.)

:done
echo.
pause
exit /b 0

:fail
echo.
echo  ============================================================
echo   Build FAILED — check errors above.
echo  ============================================================
pause
exit /b 1
