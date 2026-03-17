#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Google Maps Scraper — macOS Build Script
# Author:   Soubarna Karmakar  |  Copyright © 2025. All rights reserved.
# Produces: dist/GoogleMapsScraper.app  +  dist/GoogleMapsScraper_v2.0.dmg
#
# Requirements:
#   • macOS 10.14+
#   • Python 3.10+  (brew install python or https://python.org)
#   • Xcode Command Line Tools:  xcode-select --install
#   • Internet access (pip downloads)
#
# Usage:
#   chmod +x build_mac.sh
#   ./build_mac.sh
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

APP_NAME="GoogleMapsScraper"
APP_DISPLAY="Google Maps Scraper"
VERSION="2.0"
BUNDLE_ID="com.googlemapsscraper.app"

DIST_DIR="dist"
DMG_STAGING="dmg_staging"
DMG_OUT="${DIST_DIR}/${APP_NAME}_v${VERSION}_macOS.dmg"

BOLD='\033[1m'; CYAN='\033[0;36m'; GREEN='\033[0;32m'
YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

banner() { echo -e "\n${CYAN}${BOLD}[BUILD] $*${NC}"; }
ok()     { echo -e "${GREEN}  ✓  $*${NC}"; }
warn()   { echo -e "${YELLOW}  ⚠  $*${NC}"; }
fail()   { echo -e "${RED}  ✗  $*${NC}"; exit 1; }

# ── 0. Sanity checks ──────────────────────────────────────────────────────────
banner "Checking environment"

command -v python3 >/dev/null 2>&1 || fail "python3 not found. Install from https://python.org"
PY=$(python3 --version)
ok "Python: $PY"

command -v pip3 >/dev/null 2>&1 || fail "pip3 not found."
ok "pip3 found"

# Warn if running on Apple Silicon — build will be arm64 only unless
# a universal Python is used.
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
    warn "Building on Apple Silicon (arm64). The .app will only run on arm64 Macs."
    warn "For a universal binary, use a universal Python from https://python.org"
else
    ok "Architecture: $ARCH"
fi

# ── 1. Install Python dependencies ───────────────────────────────────────────
banner "Installing Python dependencies"
pip3 install -r requirements.txt --quiet --upgrade
ok "Dependencies installed"

# ── 2. Build React frontend ────────────────────────────────────────────────────
banner "Building React UI (shadcn/ui + Cosmic Night)"
command -v node >/dev/null 2>&1 || fail "Node.js not found. Install from https://nodejs.org"
cd frontend
npm install --silent
npm run build --silent
cd ..
ok "React build complete (frontend/dist/)"

banner "Installing PyInstaller"
pip3 install pyinstaller --quiet --upgrade
PYINST=$(pyinstaller --version)
ok "PyInstaller $PYINST"

# ── 3. Ensure Playwright Chromium is present ───────────────────────────────────
banner "Installing Playwright Chromium"
python3 -m playwright install chromium || warn "Browser install incomplete — continuing"

# ── 4. Build the .app bundle ──────────────────────────────────────────────────
banner "Building .app bundle with PyInstaller"
pyinstaller app.spec --clean --noconfirm

APP_BUNDLE="${DIST_DIR}/${APP_NAME}.app"
[[ -d "$APP_BUNDLE" ]] || fail ".app bundle not found at $APP_BUNDLE"
ok "Bundle created: $APP_BUNDLE"

# ── 4. Optional: ad-hoc code signing (no developer account required) ──────────
banner "Code signing (ad-hoc)"
if command -v codesign >/dev/null 2>&1; then
    codesign --force --deep --sign - "$APP_BUNDLE" 2>/dev/null \
        && ok "Ad-hoc signature applied (not notarised)" \
        || warn "codesign failed — users may need to right-click → Open"
else
    warn "codesign not found — skipping"
fi

# ── 5. Build the DMG ─────────────────────────────────────────────────────────
banner "Creating DMG disk image"

rm -rf "$DMG_STAGING"
mkdir -p "$DMG_STAGING"

# Copy .app into staging
cp -R "$APP_BUNDLE" "$DMG_STAGING/"

# Symlink to /Applications so users can drag-and-drop to install
ln -sf /Applications "$DMG_STAGING/Applications"

# Optional background image — skip gracefully if not present
BACKGROUND="assets/dmg_background.png"
if [[ -f "$BACKGROUND" ]]; then
    mkdir -p "$DMG_STAGING/.background"
    cp "$BACKGROUND" "$DMG_STAGING/.background/background.png"
    ok "Background image added"
fi

# Create a read-write DMG, set window appearance, then convert to read-only
TMP_DMG="${DIST_DIR}/${APP_NAME}_tmp.dmg"

hdiutil create \
    -volname "$APP_DISPLAY" \
    -srcfolder "$DMG_STAGING" \
    -ov -format UDRW \
    -size 800m \
    "$TMP_DMG"

# Mount, tweak window appearance via AppleScript, unmount
MOUNT_DIR=$(hdiutil attach -readwrite -noverify -noautoopen "$TMP_DMG" \
    | awk 'END{print $NF}')

sleep 2

osascript <<APPLESCRIPT
tell application "Finder"
    tell disk "$APP_DISPLAY"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {400, 100, 900, 430}
        set viewOptions to the icon view options of container window
        set arrangement of viewOptions to not arranged
        set icon size of viewOptions to 100
        set position of item "${APP_NAME}.app" of container window to {140, 160}
        set position of item "Applications" of container window to {380, 160}
        close
        open
        update without registering applications
        delay 2
    end tell
end tell
APPLESCRIPT

sync
hdiutil detach "$MOUNT_DIR" -quiet

# Convert to compressed read-only DMG
hdiutil convert "$TMP_DMG" -format UDZO -imagekey zlib-level=9 -o "$DMG_OUT"
rm -f "$TMP_DMG"
rm -rf "$DMG_STAGING"

ok "DMG created: $DMG_OUT"

# ── 6. Summary ───────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${GREEN}  Build complete!${NC}"
echo -e "  App bundle:  ${DIST_DIR}/${APP_NAME}.app"
echo -e "  Installer:   ${DMG_OUT}"
echo -e "${BOLD}${GREEN}════════════════════════════════════════════════════${NC}"
echo ""
echo "  NOTE: The first time the app is launched, it will"
echo "  automatically download the Chromium browser (~120 MB)."
echo ""
if [[ "$ARCH" == "arm64" ]]; then
    echo "  GATEKEEPER: If macOS blocks the app, right-click → Open"
    echo "  OR run:  xattr -d com.apple.quarantine dist/${APP_NAME}.app"
fi
echo ""
