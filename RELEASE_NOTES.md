# Scrappy — Release Notes

---

## v2.0.1 — 17 March 2026

> **Author:** Soubarna Karmakar
> **Platform:** Windows 10/11
> **License:** Proprietary — free to use, not open source

---

### Bug Fixes & Improvements

#### Export to Excel
- Fixed a crash where `openpyxl.Workbook.close()` was called after saving — this method does not exist in most openpyxl versions and caused the export endpoint to return HTTP 500.
- Changed export strategy: instead of streaming the file through the browser (blocked by the native window), the server now saves the `.xlsx` directly to your **Downloads folder** and opens it automatically in Excel. The status bar confirms the filename.

#### Scraped Data Quality
- All extracted text fields (Name, Address, Category) are now sanitised to remove Unicode icon/symbol characters that Google Maps injects into its DOM — these appeared as stray icons in the Address column and in exported files.
- Text is normalised to NFKC and all control, format, private-use, and symbol Unicode categories are stripped before display and export.

#### Installer & Executable
- Renamed the executable from `GoogleMapsScraper.exe` to **`Scrappy.exe`** — it now appears correctly in Task Manager, Services, and Windows Explorer.
- Fixed the Inno Setup installer source path (`dist\Scrappy\*`) so the correct executable is packaged.
- Fixed a startup crash on new machines: uvicorn raised `ValueError: Unable to configure formatter 'default'` when launched from a PyInstaller bundle. Resolved by passing `log_config=None` to `uvicorn.run()`.
- `tkinter` is now bundled in the executable (it was previously excluded), enabling error and fallback dialogs to appear on screen.

---

### Native Window vs Browser Fallback

Scrappy opens as a **native desktop window** by default. If the native window cannot be initialised, it falls back to your **default browser** and shows a small status dialog.

#### When you get a native window
The native window uses **Microsoft Edge WebView2**, which is built into Windows 10 (v1803+) and all versions of Windows 11. You get a native window automatically when:

- You are on **Windows 10 (version 1803 or later)** or **Windows 11**
- **Microsoft Edge** is installed (it ships with Windows and keeps WebView2 up to date)
- The installer ran successfully — it silently installs the WebView2 Runtime bootstrapper on machines that don't already have it

#### When it falls back to the browser
If WebView2 is unavailable (e.g. a heavily locked-down corporate machine or an outdated Windows build), Scrappy will:

1. Open the app UI in your **default web browser** automatically
2. Show a small **"Scrappy is running"** dialog with the local URL and an **Open in Browser** button
3. Continue running normally — all features work identically in the browser

To force a native window on a machine where WebView2 is missing, install it manually:
**Settings → Windows Update → Optional Updates**, or download the runtime directly from Microsoft.

---

### Downloads

| File | Platform |
|---|---|
| `Scrappy_Setup_v2.0.exe` | Windows 10/11 (64-bit) |

> No Python, Node.js, or browser installation required — everything is bundled.

---

### System Requirements

- Windows 10 (version 1803+) or Windows 11, 64-bit
- 4 GB RAM minimum (8 GB recommended for large queries)
- 500 MB free disk space
- Internet connection for scraping

---

### Quick Usage Guide

1. Launch **Scrappy** from the Desktop shortcut or Start Menu
2. Enter search queries in the left panel — one per line, e.g.:
   ```
   IT Companies in Koramangala
   Restaurants in Bandra
   Law firms in Connaught Place
   ```
3. Toggle options as needed:
   - **Run browser in background** — hides the Chromium window during scraping
   - **Extract emails from websites** — fetches contact emails (adds ~5–10 s per place)
   - **Phone numbers only** — skips leads with no phone number
   - **Deduplicate leads** — if the same Name + Phone appears across queries, keeps only the latest result
4. Click **Start Scraping**
5. Watch results appear live in the table
6. Click **Export to Excel** — the file saves to your Downloads folder and opens in Excel automatically

---

### Known Limitations

- **Google selector changes** — Google Maps occasionally updates its HTML. If scraping stops working, check the [Issues](https://github.com/soubarnak/scrappy/issues) page for an update.
- **Email extraction is slow** — each website fetch adds 5–10 seconds per business. Disable it for faster bulk scraping.
- **Rate limiting** — for very large queries (1000+ results), Google may slow responses temporarily. The scraper uses human-like delays to minimise this.

---

### Changelog

```
v2.0.1  2026-03-17  Bug fixes: export, installer rename, unicode cleanup, startup crash
v2.0    2025-03-17  First public release — FastAPI + React + Playwright desktop app
v1.0    internal    Proof of concept — Selenium + basic Tkinter + CSV only
```

---

### Reporting Bugs

Found an issue? Please open a GitHub Issue and include:

1. Your Windows version (e.g. Windows 11 23H2)
2. The exact search query that caused the problem
3. A screenshot of the error or status bar message

**[Open a Bug Report](https://github.com/soubarnak/scrappy/issues/new)**

---

### Author

**Soubarna Karmakar**
GitHub: [@soubarnak](https://github.com/soubarnak)

---

> This software is provided for personal and professional data research use.
> Respect Google's Terms of Service and applicable data privacy laws in your region.
> The author accepts no liability for misuse of this tool.
