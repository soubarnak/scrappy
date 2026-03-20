@echo off
:: Scrappy -- Windows Build Script
:: Produces a fully self-contained installer:
::   installer_output\Scrappy_Setup_v2.0.exe
::
:: Bundled in the installer:
::   - Python runtime + all packages  (PyInstaller)
::   - React frontend                 (pre-built static files)
::   - Playwright Chromium browser    (~130 MB)
::   - Microsoft Edge WebView2        Standalone Installer (fully offline, ~170 MB)
::
:: Developer requirements:
::   - Python 3.x    https://python.org
::   - Node.js 18+   https://nodejs.org
::   - Inno Setup 6  https://jrsoftware.org/isdl.php
::
:: Author: Soubarna Karmakar
setlocal EnableDelayedExpansion
title Scrappy -- Windows Build
color 0B
cd /d "%~dp0"

echo.
echo  ============================================================
echo   Scrappy v2.0 -- Windows Build
echo   Author: Soubarna Karmakar
echo   Output: installer_output\Scrappy_Setup_v2.0.exe
echo  ============================================================
echo.

:: Pre-flight
python --version >/dev/null 2>&1 || ( echo [ERROR] Python not found. Get it from https://python.org & goto :fail )
node   --version >/dev/null 2>&1 || ( echo [ERROR] Node.js not found. Get it from https://nodejs.org  & goto :fail )

echo.
echo  [1/6] Installing Python dependencies...
pip install -r requirements.txt --quiet --upgrade
if errorlevel 1 ( echo [ERROR] pip install failed. & goto :fail )

pip install pywebview comtypes --quiet 2>/dev/null
echo  [OK] pywebview + comtypes installed (native WebView2 window)

pip install pyinstaller --quiet --upgrade
if errorlevel 1 ( echo [ERROR] PyInstaller install failed. & goto :fail )

echo.
echo  [2/6] Building React frontend...
cd frontend
call npm install --silent
if errorlevel 1 ( echo [ERROR] npm install failed. & cd .. & goto :fail )
call npm run build --silent
if errorlevel 1 ( echo [ERROR] npm build failed.    & cd .. & goto :fail )
cd ..
echo  [OK] React build complete.

echo.
echo  [3/6] Installing Playwright Chromium browser...
python -m playwright install chromium
if errorlevel 1 ( echo [WARNING] Chromium install may have failed. Continuing... )

echo.
echo  [4/6] Building standalone exe with PyInstaller...
echo        (First run can take 5-10 minutes)
pyinstaller app.spec --clean --noconfirm
if errorlevel 1 ( echo [ERROR] PyInstaller failed. & goto :fail )
echo  [OK] exe built -- dist\Scrappy\Scrappy.exe

echo.
echo  [5/6] Bundling Playwright Chromium into dist\...
set "PW_CACHE=%LOCALAPPDATA%\ms-playwright"
set "PW_DEST=dist\Scrappy\_playwright_browsers"
mkdir "%PW_DEST%" 2>/dev/null
set "CHROMIUM_FOUND=0"
for /d %%D in ("%PW_CACHE%\chromium-*") do (
    echo  Copying %%~nxD...
    xcopy "%%D" "%PW_DEST%\%%~nxD\" /E /I /Q /Y >/dev/null
    set "CHROMIUM_FOUND=1"
)
if "!CHROMIUM_FOUND!"=="1" (
    echo  [OK] Chromium bundled. End-users need no internet on first launch.
) else (
    echo  [WARNING] Chromium not found at %PW_CACHE%
    echo            Run:  python -m playwright install chromium
    echo            Then re-run this script.
)

echo.
echo  [5b] Downloading WebView2 Standalone Installer (~170 MB)...
echo       This is a one-time download cached in redist\
mkdir redist 2>/dev/null
if not exist "redist\MicrosoftEdgeWebView2RuntimeInstallerX64.exe" (
    echo  Querying Microsoft Edge Enterprise API for latest version...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop';try{$api=Invoke-RestMethod 'https://edgeupdates.microsoft.com/api/products?view=enterprise';$wv2=$api|Where-Object{$_.Product -eq 'WebView2Runtime'};$rel=($wv2.Releases|Where-Object{$_.Platform -eq 'Windows' -and $_.Architecture -eq 'x64'})[0];$art=($rel.Artifacts|Where-Object{$_.ArtifactName -match 'standalone|exe'})[0];if(-not $art){throw 'Artifact not found in API response'};Write-Host('  Version: '+$rel.ProductVersion);Invoke-WebRequest $art.Location -OutFile 'redist\MicrosoftEdgeWebView2RuntimeInstallerX64.exe' -UseBasicParsing;Write-Host '  [OK] Standalone installer saved to redist\'}catch{Write-Warning('API download failed: '+$_);Write-Host '  Falling back to online bootstrapper (end-users will need internet)...';Invoke-WebRequest 'https://go.microsoft.com/fwlink/p/?LinkId=2124703' -OutFile 'redist\MicrosoftEdgeWebView2RuntimeInstallerX64.exe' -UseBasicParsing;Write-Host '  [FALLBACK] Bootstrapper saved to redist\'}"
    if errorlevel 1 (
        echo  [WARNING] WebView2 download failed. Re-run this script to retry.
        echo            The installer will still work but end-users will need internet.
    )
) else (
    echo  [OK] WebView2 standalone installer already cached -- skipping download.
)

echo.
echo  ============================================================
echo   Executable ready:
echo     dist\Scrappy\Scrappy.exe
echo  ============================================================

echo.
echo  [6/6] Checking for Inno Setup 6...
set "ISCC="
for %%P in (
    "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
    "%ProgramFiles%\Inno Setup 6\ISCC.exe"
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    "C:\Program Files\Inno Setup 6\ISCC.exe"
) do (
    if exist "%%~P" ( set "ISCC=%%~P" & goto :found_iscc )
)
goto :no_iscc

:found_iscc
echo  [OK] Inno Setup found -- building installer...
mkdir installer_output 2>/dev/null
"%ISCC%" installer.iss
if errorlevel 1 (
    echo  [WARNING] Inno Setup build failed. The exe in dist\ is still usable.
    goto :done
)
echo.
echo  ============================================================
echo   Installer ready:
echo     installer_output\Scrappy_Setup_v2.0.exe
echo.
echo   Fully self-contained:
echo     - No Python needed on end-user machine
echo     - No Node.js needed
echo     - No internet needed (WebView2 + Chromium bundled)
echo   Upload to GitHub Releases!
echo  ============================================================
goto :done

:no_iscc
echo  [INFO] Inno Setup 6 not found -- skipping installer packaging.
echo         Download from: https://jrsoftware.org/isdl.php
echo         After installing Inno Setup, re-run this script.

:done
echo.
pause
exit /b 0

:fail
echo.
echo  ============================================================
echo   BUILD FAILED -- see errors above.
echo  ============================================================
pause
exit /b 1
