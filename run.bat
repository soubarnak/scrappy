@echo off
:: Google Maps Scraper — Launch Script
:: Author    : Soubarna Karmakar
:: Copyright : (c) 2025 Soubarna Karmakar. All rights reserved.
title Google Maps Scraper
cd /d "%~dp0"

echo  Starting Google Maps Scraper by Soubarna Karmakar...
python app.py
if errorlevel 1 (
    echo.
    echo  [ERROR] App exited with an error.
    echo  Make sure you ran install.bat first.
    pause
)
