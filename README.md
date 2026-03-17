# 🗺 Google Maps Scraper

**Extract business data from Google Maps — no API key, no login, no limits.**

> Built and maintained by **[Soubarna Karmakar](https://github.com/soubarna)**
>
> © 2025 Soubarna Karmakar. All rights reserved.

---

## ✨ Features

| Feature | Details |
|---|---|
| **No API key needed** | Works directly with Google Maps — zero credentials |
| **No login required** | Fully anonymous, browser-based extraction |
| **Multi-query support** | Run dozens of queries in one session |
| **Bulk scraping** | Scrolls until the last result — no artificial caps |
| **Live results table** | See data appear in real time as it's scraped |
| **Excel export** | Styled .xlsx with Summary sheet, auto-filter, freeze pane |
| **Email extraction** | Optionally visits each website to find contact emails |
| **Modern dark UI** | Clean CustomTkinter interface — dark theme, sortable table |
| **Filter & copy** | Filter live, right-click to copy any field or row |

### Data extracted per business
`Name` · `Address` · `Category` · `Phone` · `Website` · `Email` · `Query`

---

## 📸 Screenshots

> <img width="1919" height="1028" alt="image" src="https://github.com/user-attachments/assets/5f934bf9-e3c9-4358-b1a6-d36586b64c32" />


---

## 💾 Download & Install

### Windows

1. Go to [**Releases**](../../releases/latest)
2. Download `GoogleMapsScraper_Setup_v2.0.exe`
3. Run the installer — no admin rights required
4. Launch from your Desktop or Start Menu

> **First launch:** the app will automatically download the Chromium browser (~120 MB). An internet connection is required for this one-time step.

---

### macOS

1. Go to [**Releases**](../../releases/latest)
2. Download `GoogleMapsScraper_v2.0_macOS.dmg`
3. Open the DMG, drag **Google Maps Scraper** into **Applications**
4. Double-click to launch

> **Gatekeeper warning?** Right-click the app → **Open**, then click Open again.
> Or run in Terminal: `xattr -d com.apple.quarantine /Applications/GoogleMapsScraper.app`

> **First launch:** same as Windows — Chromium (~120 MB) is downloaded automatically.

---

### Run from source (Windows / macOS / Linux)

**Prerequisites:** Python 3.10+

```bash
# 1. Clone the repo
git clone https://github.com/soubarnak/google-maps-scraper.git
cd google-maps-scraper

# 2. Install dependencies  (Windows: use install.bat instead)
pip install -r requirements.txt
python -m playwright install chromium

# 3. Launch
python scraper.py
```

On **Windows** you can also just double-click:
- `install.bat` — first-time setup
- `run.bat` — launch the app

---

## 🚀 How to Use

### Step 1 — Enter your search queries
In the **Search Queries** box on the left, type one query per line:

```
IT Companies in Koramangala
Restaurants near Bandra
Dental Clinics in Pune
Chartered Accountants in Chennai
```

### Step 2 — Choose settings

| Setting | When to enable |
|---|---|
| **Run browser in background** | Faster; no visible browser window |
| **Extract emails from websites** | Visits each website to find contact email (~8 s per place) |

### Step 3 — Start scraping
Click **▶ Start Scraping**. Results appear in the table in real time.

### Step 4 — Filter & review
Use the **Filter** bar to search across all fields instantly.
Click any column header to sort. Right-click a row for copy/delete options.

### Step 5 — Export
Click **📥 Export to Excel** to save a formatted `.xlsx` file with:
- **Maps Data** sheet — all records, styled, with auto-filter
- **Summary** sheet — timestamp, total count, per-query breakdown

---

## 📋 System Requirements

| | Minimum |
|---|---|
| **Windows** | Windows 10 / 11 (64-bit) |
| **macOS** | macOS 10.14 Mojave or later |
| **RAM** | 2 GB |
| **Disk** | 500 MB free (Chromium ~300 MB + app ~150 MB) |
| **Internet** | Required for scraping + one-time Chromium download |

---

## ❓ FAQ

**Q: Does it require a Google account?**
No. The scraper opens Google Maps like a regular browser visitor.

**Q: Does it use the Google Maps API?**
No. No API key, no billing, no rate limits.

**Q: Will it get blocked?**
The scraper uses stealth techniques to mimic a real user. For very large scrapes, consider enabling **background mode** and adding natural pauses between queries.

**Q: Why is Chromium downloaded on first run?**
Chromium is the browser that the scraper controls. It's downloaded once (~120 MB) and reused for all future scrapes.

**Q: Email extraction is slow — why?**
For each business, the scraper visits the website and scans it for email addresses. Each visit takes a few seconds. Disable this option if you only need the Google Maps data.

**Q: Can I run this on Linux?**
Yes, via the **run from source** method. No pre-built Linux binary is provided.

---

## 🐛 Bug Reports & Feature Requests

Found a bug or have a suggestion? Please open a GitHub Issue:

- [🐛 Report a Bug](../../issues/new?template=bug_report.yml)
- [💡 Request a Feature](../../issues/new?template=feature_request.yml)

Please include your OS, Python version, and a description of what happened vs. what you expected.

---

## ⚠️ Disclaimer

This tool automates a public web interface for personal and research use. Always respect Google's Terms of Service and local data-protection laws. The author is not responsible for misuse.

---

## 👤 Author

**Soubarna Karmakar**
© 2025 — All rights reserved.

See [LICENSE](LICENSE) for usage terms.
