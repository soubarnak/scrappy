# How to Push Google Maps Scraper to GitHub
### Step-by-step with screenshots descriptions
**By Soubarna Karmakar**

---

## PART 1 — Create the Repository on GitHub.com

---

### Step 1 — Sign in to GitHub

Open your browser and go to **https://github.com/login**

```
┌─────────────────────────────────────────────┐
│  github.com/login                           │
│                                             │
│  Username or email:  [ soubarnak         ] │
│  Password:           [ ***************** ] │
│                                             │
│           [ Sign in ]                       │
└─────────────────────────────────────────────┘
```

Enter your username **soubarnak** and your password, then click **Sign in**.

---

### Step 2 — Go to "New Repository"

After signing in you will see your GitHub dashboard.

Click the **"+"** icon in the top-right corner of the screen → then click **"New repository"**

```
┌─────────────────────────────────────────────────────────┐
│  github.com                            [+▼]  [👤▼]     │
│                                         │               │
│                                    ┌────┴──────────┐    │
│                                    │ New repository │◄── CLICK THIS
│                                    │ Import repo   │    │
│                                    │ New gist      │    │
│                                    └───────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

### Step 3 — Fill in the repository details

You will land on **github.com/new** — fill it in exactly like this:

```
┌──────────────────────────────────────────────────────────────┐
│  Create a new repository                                     │
│                                                              │
│  Owner                    Repository name                    │
│  [ soubarnak ▼ ]    /    [ google-maps-scraper        ]  ←  TYPE THIS
│                                                              │
│  Description (optional)                                      │
│  [ Extract business data from Google Maps — no API key  ]  ←  TYPE THIS
│                                                              │
│  ○ Public   ← SELECT THIS                                    │
│    Anyone on the internet can see this repository            │
│                                                              │
│  ● Private                                                   │
│                                                              │
│  Initialize this repository with:                           │
│  □ Add a README file          ← LEAVE UNCHECKED             │
│  □ Add .gitignore             ← LEAVE UNCHECKED             │
│  □ Choose a license           ← LEAVE UNCHECKED             │
│                                                              │
│               [ Create repository ]  ← CLICK THIS          │
└──────────────────────────────────────────────────────────────┘
```

**Important:** Leave all three checkboxes (README, .gitignore, license) **unchecked** — we already have these files locally.

---

### Step 4 — Copy your repository URL

After clicking **Create repository**, GitHub shows you an empty repo page.

```
┌──────────────────────────────────────────────────────────────┐
│  soubarnak / google-maps-scraper                             │
│                                                              │
│  Quick setup — if you've done this kind of thing before      │
│                                                              │
│  HTTPS  [ https://github.com/soubarnak/google-maps-scraper ] │
│                                              [📋 copy]  ← CLICK TO COPY
│                                                              │
│  …or push an existing repository from the command line       │
│                                                              │
│  git remote add origin https://github.com/soubarnak/         │
│    google-maps-scraper.git                                   │
│  git branch -M main                                          │
│  git push -u origin main                                     │
└──────────────────────────────────────────────────────────────┘
```

The remote is already set correctly — you do NOT need to run `git remote add` again.

---

## PART 2 — Create a Personal Access Token (PAT)

GitHub no longer accepts your account password for `git push`. You need a token.

---

### Step 5 — Open Developer Settings

Click your **profile picture** (top-right) → **Settings**

```
┌──────────────────────────────────┐
│  [👤▼]                          │
│  ┌──────────────────────────┐   │
│  │ Your profile             │   │
│  │ Your repositories        │   │
│  │ ─────────────────────── │   │
│  │ Settings             ◄───┼── CLICK THIS
│  └──────────────────────────┘   │
└──────────────────────────────────┘
```

---

### Step 6 — Go to Developer Settings

On the Settings page, scroll all the way to the **bottom** of the left sidebar and click **"Developer settings"**

```
Left sidebar (scroll to bottom):
┌──────────────────────────┐
│  Profile                 │
│  Account                 │
│  Appearance              │
│  Accessibility           │
│  ...                     │
│  ─────────────────────── │
│  Developer settings  ◄── CLICK THIS (very bottom)
└──────────────────────────┘
```

---

### Step 7 — Create a Personal Access Token

Inside Developer Settings:

Click **"Personal access tokens"** → **"Tokens (classic)"** → **"Generate new token"** → **"Generate new token (classic)"**

```
┌──────────────────────────────────────────────────────────────┐
│  Developer settings                                          │
│                                                              │
│  GitHub Apps                                                 │
│  OAuth Apps                                                  │
│  Personal access tokens                                      │
│    ├─ Fine-grained tokens                                    │
│    └─ Tokens (classic)   ◄── CLICK THIS                     │
└──────────────────────────────────────────────────────────────┘
```

Then click **"Generate new token (classic)"**:

```
┌──────────────────────────────────────────────────────────────┐
│  Personal access tokens (classic)                            │
│                                   [ Generate new token ▼ ]  │
│                                     ├─ Generate new token    │
│                                     └─ Generate new token    │
│                                          (classic)  ◄── CLICK
└──────────────────────────────────────────────────────────────┘
```

---

### Step 8 — Configure the token

Fill in the form:

```
┌──────────────────────────────────────────────────────────────┐
│  New personal access token (classic)                         │
│                                                              │
│  Note (name for the token):                                  │
│  [ google-maps-scraper-push              ]  ← TYPE THIS     │
│                                                              │
│  Expiration:  [ 90 days ▼ ]  (or "No expiration")          │
│                                                              │
│  Select scopes:                                              │
│  ☑ repo   ← TICK THIS (full repository access)             │
│    ├─ repo:status                                            │
│    ├─ repo_deployment                                        │
│    ├─ public_repo                                            │
│    └─ repo:invite                                            │
│                                                              │
│              [ Generate token ]  ← CLICK THIS               │
└──────────────────────────────────────────────────────────────┘
```

---

### Step 9 — Copy the token IMMEDIATELY

GitHub shows the token **only once**. Copy it now.

```
┌──────────────────────────────────────────────────────────────┐
│  ✅ Make sure to copy your personal access token now.        │
│     You won't be able to see it again!                       │
│                                                              │
│  [ ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx ]  [📋]  ← COPY │
└──────────────────────────────────────────────────────────────┘
```

Save it somewhere safe (e.g. Notepad) — you'll paste it as your password.

---

## PART 3 — Push from PowerShell / Command Prompt

---

### Step 10 — Open PowerShell in your project folder

Press **Win + X** → click **"Terminal"** or **"PowerShell"**

Then navigate to the project folder:

```powershell
cd "C:\Users\souba\Documents\Claude\Scraper"
```

---

### Step 11 — Check your current git status

```powershell
git status
```

Expected output:
```
On branch main
nothing to commit, working tree clean
```

If you see uncommitted changes, run:
```powershell
git add .
git commit -m "Ready to publish"
```

---

### Step 12 — Push to GitHub

```powershell
git push -u origin main
```

Git will prompt for credentials:

```
┌─────────────────────────────────────────────────────┐
│  Username for 'https://github.com':                 │
│  > soubarnak                        ← TYPE THIS    │
│                                                     │
│  Password for 'https://soubarnak@github.com':       │
│  > ghp_xxxx...                      ← PASTE TOKEN  │
└─────────────────────────────────────────────────────┘
```

**Important:** When you paste the token, nothing will appear on screen (it's hidden). Just paste and press Enter.

Expected success output:
```
Enumerating objects: 28, done.
Counting objects: 100% (28/28), done.
Writing objects: 100% (28/28), 52.34 KiB | 2.61 MiB/s, done.
Total 28 (delta 0), reused 0 (delta 0)
To https://github.com/soubarnak/google-maps-scraper.git
 * [new branch]      main -> main
Branch 'main' set up to track remote origin/main.
```

---

### Step 13 — Verify on GitHub

Open your browser and go to:
**https://github.com/soubarnak/google-maps-scraper**

You should see all your files listed, and the README rendered below:

```
┌──────────────────────────────────────────────────────────────┐
│  soubarnak / google-maps-scraper                  ⭐ Star   │
│  ─────────────────────────────────────────────────────────  │
│  📄 scraper.py                                              │
│  📄 requirements.txt                                        │
│  📄 install.bat                                             │
│  📄 run.bat                                                 │
│  📄 build_windows.bat                                       │
│  📄 installer.iss                                           │
│  📄 README.md                                               │
│  📄 LICENSE                                                 │
│  📄 CHANGELOG.md                                            │
│  📄 .gitignore                                              │
│  📁 assets/                                                 │
│  📁 .github/                                                │
│  ─────────────────────────────────────────────────────────  │
│  🗺 Google Maps Scraper                                     │
│  Extract business data from Google Maps...                  │
└──────────────────────────────────────────────────────────────┘
```

---

## PART 4 — Final Repository Settings

---

### Step 14 — Add topics & description

On your repo page click the **⚙ gear icon** next to "About":

```
┌──────────────────────────────────────────┐
│  About                          [⚙]  ← CLICK
│  No description                          │
│  No website                              │
│  No topics                               │
└──────────────────────────────────────────┘
```

Fill in:
- **Description:** `Extract business data from Google Maps — no API key, no login, no limits.`
- **Topics:** `google-maps` `scraper` `python` `playwright` `tkinter` `excel` `windows` `macos`
- Click **Save changes**

---

### Step 15 — Enable Issues (for bug reports)

Go to **Settings** tab of your repo → scroll to **Features** section:

```
┌──────────────────────────────────────────┐
│  Features                                │
│  ☑ Issues    ← make sure this is ON    │
│  □ Wikis                                 │
│  □ Projects                              │
│  □ Discussions                           │
└──────────────────────────────────────────┘
```

Issues should be ON by default. This is what allows users to report bugs.

---

### Step 16 (Optional) — Create your first Release

Once you've built the installer with `build_windows.bat`:

Go to your repo → click **"Releases"** (right side) → **"Create a new release"**

```
┌──────────────────────────────────────────────────────────────┐
│  Create a new release                                        │
│                                                              │
│  Choose a tag:   [ v2.0            ]  ← TYPE THIS          │
│  Target branch:  [ main ▼          ]                        │
│  Release title:  [ Google Maps Scraper v2.0 ]  ← TYPE THIS │
│                                                              │
│  Describe this release:                                      │
│  [ Paste your CHANGELOG.md content here           ]         │
│                                                              │
│  Attach binaries:                                            │
│  [ Drop files here or click to upload ]                     │
│    ↑ Drag GoogleMapsScraper_Setup_v2.0.exe here             │
│                                                              │
│  ○ Set as the latest release                                 │
│                                                              │
│              [ Publish release ]  ← CLICK THIS              │
└──────────────────────────────────────────────────────────────┘
```

After publishing, users can click **Releases** on your repo page and download the `.exe` directly.

---

## Quick Command Reference

```powershell
# Check what's changed
git status

# Stage everything
git add .

# Commit with a message
git commit -m "your message here"

# Push to GitHub
git push

# Pull latest from GitHub
git pull
```

---

**Your repo will be live at:**
https://github.com/soubarnak/google-maps-scraper
