@echo off
title Google Maps Scraper
cd /d "%~dp0"
python scraper.py
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] The application exited with an error.
    echo  Make sure you ran install.bat first.
    pause
)
