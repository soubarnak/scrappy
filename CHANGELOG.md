# Changelog

All notable changes to **Google Maps Scraper** are documented here.

> **Author:** Soubarna Karmakar
> **Format:** [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

---

## [2.0] — 2025-03-17

### Added
- Complete rewrite with **Playwright** browser engine (replaces Selenium)
- Stealth JS injection to avoid bot-detection
- Two-phase scraping: collect all URLs first, then extract data
- `_ensure_browser()` — auto-downloads Chromium on first run (PyInstaller-safe)
- **Multi-query support** — enter one query per line, all processed sequentially
- Live results table with real-time row insertion
- **Filter bar** — search across all columns instantly
- Sortable columns (click header to sort)
- Right-click context menu: copy Name / Phone / Website / Email / full row
- Double-click any cell to copy its value
- Stats panel (Total Found · With Website)
- **Email extraction** from business websites (optional toggle)
- **Excel export** with styled Data sheet + Summary sheet (auto-filter, freeze pane)
- Windows installer via **Inno Setup 6** (`installer.iss`)
- macOS DMG via **hdiutil** (`build_mac.sh`)
- PyInstaller spec files for Windows (`scraper.spec`) and macOS (`scraper_mac.spec`)
- Icon generator (`create_icon.py`) — produces `.ico`, `.png`, `.icns`
- `install.bat` / `run.bat` for quick setup without building an installer
- Author credit (Soubarna Karmakar) embedded in all files

### Changed
- UI framework: switched to **CustomTkinter** dark theme (from plain Tkinter)
- Scraper engine: **Playwright** sync API (was Selenium + undetected-chromedriver)
- Browser auto-install: happens at first scrape, not at app startup

---

## [1.0] — *internal prototype*

- Initial proof-of-concept with Selenium
- Basic Tkinter UI
- Single-query scraping
- CSV export only
