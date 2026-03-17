# 🗺️ Google Maps Scraper — Release Notes

---

## v2.0 — 17 March 2025

> **Author:** Soubarna Karmakar
> **Platform:** Windows 10/11 · macOS 12+
> **License:** Proprietary — free to use, not open source

---

### 🎉 What's New in v2.0

This is the first public release of **Google Maps Scraper**, a desktop application that
extracts business data from Google Maps — with no API key, no login, and no usage limits.

---

### ✨ Highlights

| Feature | Details |
|---|---|
| 🔍 **Multi-Query Scraping** | Enter multiple search queries (one per line) and run them all in one click |
| 📋 **6 Data Fields** | Name · Address · Category · Phone · Website · Email |
| 📧 **Email Extraction** | Optionally fetches emails directly from each business website |
| 📊 **Excel Export** | Styled `.xlsx` with Data sheet + Summary sheet, auto-filter & freeze pane |
| 🖥️ **Modern UI** | Dark-theme CustomTkinter interface with live results table |
| 🔎 **Instant Filter** | Search across all columns in real time |
| 🖱️ **Right-Click Menu** | Copy Name / Phone / Website / Email / full row |
| 🤖 **No Detection** | Playwright + stealth JS injection mimics real human browsing |
| 🔄 **Auto Browser Install** | Downloads Chromium automatically on first run — no manual setup |
| 🪟 **Windows Installer** | One-click `.exe` installer built with Inno Setup 6 |
| 🍎 **macOS DMG** | Drag-to-install `.dmg` with `.app` bundle |

---

### 📦 Downloads

| File | Platform | Size |
|---|---|---|
| `GoogleMapsScraper_Setup_v2.0.exe` | Windows 10/11 (64-bit) | ~85 MB |
| `GoogleMapsScraper_v2.0.dmg` | macOS 12 Monterey or later | ~90 MB |

> **No Python or browser installation required** — everything is bundled.

---

### 🖥️ System Requirements

**Windows**
- Windows 10 or Windows 11 (64-bit)
- 4 GB RAM minimum (8 GB recommended for large queries)
- 500 MB free disk space
- Internet connection

**macOS**
- macOS 12 Monterey or later
- Apple Silicon (M1/M2/M3) or Intel
- 4 GB RAM minimum
- 500 MB free disk space
- Internet connection

---

### 🚀 How to Install

#### Windows
1. Download `GoogleMapsScraper_Setup_v2.0.exe`
2. Double-click the installer
3. Follow the on-screen steps (Next → Next → Install)
4. Launch from the Desktop shortcut or Start Menu
5. On first run, Chromium browser downloads automatically (~120 MB, one time only)

#### macOS
1. Download `GoogleMapsScraper_v2.0.dmg`
2. Open the `.dmg` file
3. Drag **Google Maps Scraper.app** into your **Applications** folder
4. Right-click the app → **Open** (needed only the very first time on macOS)
5. On first run, Chromium browser downloads automatically (~120 MB, one time only)

#### Run from Source (Windows/macOS/Linux)
```bash
# 1. Clone the repo
git clone https://github.com/soubarnak/google-maps-scraper.git
cd google-maps-scraper

# 2. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 3. Launch
python scraper.py
```

---

### 📖 Quick Usage Guide

1. **Launch** the application
2. **Enter queries** in the left panel — one per line, e.g.:
   ```
   IT Companies in Koramangala
   Restaurants in Bandra
   Law firms in Connaught Place
   ```
3. **Toggle options:**
   - ☑ *Run browser in background* — faster, no visible browser window
   - ☑ *Extract emails from websites* — slower but finds contact emails
4. Click **▶ Start Scraping**
5. Watch results appear live in the table
6. Use the **Filter bar** to search within results
7. Click **📥 Export to Excel** to save your data

---

### ⚠️ Known Limitations

- **Google selector changes** — Google Maps occasionally updates its HTML structure.
  If scraping stops working, check the [Issues](https://github.com/soubarnak/google-maps-scraper/issues) page for an update.
- **Email extraction is slow** — each website fetch adds ~5–10 seconds per business.
  Disable it for faster bulk scraping.
- **Rate limiting** — for very large queries (1000+ results), Google may temporarily
  slow responses. The scraper uses human-like delays to minimise this.
- **macOS Gatekeeper** — you must right-click → Open the first time due to Apple's
  notarisation requirement for non-App Store apps.
- **Headless mode on Windows** — if you see a blank browser, switch to
  *Run browser in background* = OFF for better compatibility.

---

### 🐛 Reporting Bugs

Found an issue? Please open a GitHub Issue and include:

1. Your operating system (e.g. Windows 11, macOS 14)
2. The exact search query that caused the problem
3. A screenshot of the error (if any)
4. The status bar message shown in the app

👉 **[Open a Bug Report](https://github.com/soubarnak/google-maps-scraper/issues/new)**

---

### 🔮 Planned for v2.1

- [ ] Duplicate detection across queries
- [ ] Pause / Resume scraping
- [ ] CSV export option
- [ ] Proxy support
- [ ] Column visibility toggle
- [ ] Dark / Light theme switch

---

### 📜 Changelog Summary

```
v2.0  2025-03-17  First public release — full rewrite with Playwright + CustomTkinter
v1.0  internal    Proof of concept — Selenium + basic Tkinter + CSV only
```

Full changelog: [CHANGELOG.md](./CHANGELOG.md)

---

### 👩‍💻 Author

**Soubarna Karmakar**
GitHub: [@soubarnak](https://github.com/soubarnak)

---

> This software is provided for personal and professional data research use.
> Respect Google's Terms of Service and applicable data privacy laws in your region.
> The author accepts no liability for misuse of this tool.
