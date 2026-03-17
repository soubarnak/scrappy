# GitHub Repository Setup Guide

> **How to publish Google Maps Scraper on GitHub so others can use it and report bugs.**
>
> Follow these steps once. After that, every future update is just a `git push`.

---

## Prerequisites

- A free [GitHub account](https://github.com/join)
- Git installed on your machine

### Install Git (if you haven't already)

**Windows:** Download and run the installer from https://git-scm.com/download/win
Accept all defaults. Tick *"Add Git to PATH"*.

**macOS:**
```bash
xcode-select --install
```
Or install via Homebrew: `brew install git`

Verify:
```bash
git --version
```

---

## Step 1 — Configure Git with your identity

Open a terminal (Command Prompt / PowerShell on Windows, Terminal on macOS):

```bash
git config --global user.name  "Soubarna Karmakar"
git config --global user.email "your-email@example.com"
```

Replace the email with the one you used to sign up to GitHub.

---

## Step 2 — Create the GitHub repository

1. Log in to [github.com](https://github.com)
2. Click the **+** icon (top-right) → **New repository**
3. Fill in the form:

   | Field | Value |
   |---|---|
   | **Repository name** | `google-maps-scraper` |
   | **Description** | Extract business data from Google Maps — no API key, no login |
   | **Visibility** | **Public** ✓ *(so others can view and report issues)* |
   | **Initialize with README** | **NO** *(we already have one)* |
   | **Add .gitignore** | **None** *(we already have one)* |
   | **Choose a license** | **None** *(we already have LICENSE)* |

4. Click **Create repository**

GitHub will show you an empty repo page with a URL like:
`https://github.com/soubarna/google-maps-scraper`

**Copy that URL** — you'll need it in Step 4.

---

## Step 3 — Initialise the local repo

Open a terminal **in your project folder** (`C:\Users\souba\Documents\Claude\Scraper`):

**Windows (PowerShell or Command Prompt):**
```bat
cd "C:\Users\souba\Documents\Claude\Scraper"
git init
git add .
git status
```

Review the list of files that will be committed. It should include:
```
scraper.py
requirements.txt
install.bat
run.bat
build_windows.bat
build_mac.sh
installer.iss
scraper.spec
scraper_mac.spec
create_icon.py
assets/icon.ico
assets/icon.png
assets/icon_1024.png
README.md
LICENSE
CHANGELOG.md
.gitignore
.github/ISSUE_TEMPLATE/bug_report.yml
.github/ISSUE_TEMPLATE/feature_request.yml
.github/ISSUE_TEMPLATE/config.yml
```

If anything looks wrong (e.g. `dist/` folder appeared), make sure `.gitignore` is in the folder and run `git status` again.

---

## Step 4 — Make the first commit and push

```bash
git commit -m "Initial release: Google Maps Scraper v2.0 by Soubarna Karmakar"
git branch -M main
git remote add origin https://github.com/soubarna/google-maps-scraper.git
git push -u origin main
```

Replace the URL with the one you copied in Step 2.

GitHub will ask for your username and password the first time.
> **Note:** GitHub no longer accepts your account password for `git push`.
> Use a **Personal Access Token** instead:
> 1. Go to GitHub → Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
> 2. Click **Generate new token (classic)**
> 3. Tick **repo** scope → Generate
> 4. Copy the token and paste it as your "password" when Git asks

---

## Step 5 — Update the config.yml link

Now that you know your GitHub URL, update one line in the issue template:

Open `.github/ISSUE_TEMPLATE/config.yml` and replace:
```yaml
url: https://github.com/YOUR_USERNAME/google-maps-scraper#readme
```
with your actual URL, e.g.:
```yaml
url: https://github.com/soubarna/google-maps-scraper#readme
```

Also update the `AppURL` in `installer.iss`:
```iss
#define AppURL "https://github.com/soubarna/google-maps-scraper"
```

Commit and push:
```bash
git add .github/ISSUE_TEMPLATE/config.yml installer.iss
git commit -m "Update issue template and installer with repo URL"
git push
```

---

## Step 6 — Configure repository settings

Go to your repo on GitHub → **Settings** tab:

### Basic settings
- **Description:** `Extract business data from Google Maps — no API key, no login, no limits.`
- **Website:** *(leave blank or add a personal site)*
- **Topics:** `google-maps`, `scraper`, `web-scraping`, `playwright`, `python`, `tkinter`, `excel`

### Features
- ✅ **Issues** — ON (this is how users report bugs)
- ❌ **Wikis** — OFF (README is enough)
- ❌ **Projects** — OFF
- ❌ **Discussions** — OFF (keep it simple)

### Social preview
- Upload a screenshot of the app as the social preview image (Settings → Social preview)

---

## Step 7 — Create a Release (so users can download the installer)

Build the installer first (run `build_windows.bat` on Windows).
Then:

1. Go to your repo → **Releases** → **Create a new release**
2. **Tag version:** `v2.0`
3. **Release title:** `Google Maps Scraper v2.0`
4. **Description:** Paste the content from `CHANGELOG.md`
5. **Attach files:**
   - `installer_output/GoogleMapsScraper_Setup_v2.0.exe` (Windows)
   - `dist/GoogleMapsScraper_v2.0_macOS.dmg` (macOS — build on a Mac)
6. Click **Publish release**

Users can now click the **Releases** link in the README to download the app.

---

## Step 8 — Future updates

Every time you change the code:

```bash
git add .
git commit -m "Fix: describe what changed"
git push
```

For a new version (e.g. v2.1):
1. Update the version number in `scraper.py`, `CHANGELOG.md`, `installer.iss`, `scraper.spec`, `scraper_mac.spec`
2. Rebuild the installers
3. Create a new GitHub Release tagged `v2.1`

---

## Quick Reference

| Task | Command |
|---|---|
| See what changed | `git status` |
| See full diff | `git diff` |
| Stage all changes | `git add .` |
| Commit | `git commit -m "message"` |
| Push to GitHub | `git push` |
| Pull latest | `git pull` |
| View history | `git log --oneline` |
