# 🗺 Scrappy — Google Maps Scraper

**Extract business data from Google Maps — no API key, no login, no limits.**

> Built and maintained by **[Soubarna Karmakar](https://github.com/soubarnak)**
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
| **Modern dark UI** | Clean React interface — dark/light theme, sortable table |
| **Deduplication** | Automatically merges duplicate results across queries |

### Data extracted per business
`Name` · `Address` · `Category` · `Phone` · `Website` · `Email` · `Rating` · `Reviews` · `Query`

---

## 📸 Screenshots

> <img width="1919" height="1028" alt="image" src="https://github.com/user-attachments/assets/5f934bf9-e3c9-4358-b1a6-d36586b64c32" />


---

## 💾 Download & Install

### Windows 10 / 11 (64-bit)

1. Go to [**Releases**](../../releases/latest)
2. Download `Scrappy_Setup_v2.0.exe`
3. Run the installer — no admin rights required
4. Launch from your Desktop or Start Menu

> Everything is bundled — no Python, Node.js, or internet connection required after install.

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
| **Run browser in background** | Hides the browser window while scraping |
| **Extract emails from websites** | Visits each website to find contact email (~8 s per place) |
| **Phone numbers only** | Skip results that have no phone number |
| **Deduplicate leads** | Merge duplicate Name + Phone entries across queries |

### Step 3 — Start scraping
Click **▶ Start Scraping**. Results appear in the table in real time.

### Step 4 — Filter & review
Use the **Filter** bar to search across all fields instantly.
Click any column header to sort.

### Step 5 — Export
Click **📥 Export to Excel** to save a formatted `.xlsx` file that opens automatically in Excel:
- **Scrappy Data** sheet — all records, styled, with auto-filter
- **Summary** sheet — timestamp and total record count

---

## 📋 System Requirements

| | |
|---|---|
| **OS** | Windows 10 (version 1803+) or Windows 11, 64-bit |
| **RAM** | 4 GB minimum (8 GB recommended for large queries) |
| **Disk** | 500 MB free |
| **Internet** | Required for scraping |

---

## ❓ FAQ

**Q: Does it require a Google account?**
No. The scraper opens Google Maps like a regular browser visitor.

**Q: Does it use the Google Maps API?**
No. No API key, no billing, no rate limits.

**Q: Will it get blocked?**
The scraper uses stealth techniques to mimic a real user. For very large scrapes, consider enabling **background mode** and adding natural pauses between queries.

**Q: Email extraction is slow — why?**
For each business, the scraper visits the website and scans it for email addresses. Each visit takes a few seconds. Disable this option if you only need the Google Maps data.

---

## 🐛 Bug Reports & Feature Requests

Found a bug or have a suggestion? Please open a GitHub Issue:

- [🐛 Report a Bug](../../issues/new?template=bug_report.yml)
- [💡 Request a Feature](../../issues/new?template=feature_request.yml)

Please include your Windows version and a description of what happened vs. what you expected.

---

## ⚠️ Disclaimer

This tool automates a public web interface for personal and research use. Always respect Google's Terms of Service and local data-protection laws. The author is not responsible for misuse.

---

## 👤 Author

**Soubarna Karmakar**
© 2025 — All rights reserved.

See [LICENSE](LICENSE) for usage terms.
