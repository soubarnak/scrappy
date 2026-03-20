#!/usr/bin/env bash
# Scrappy -- Linux (Ubuntu/Debian) Build Script
# Produces: installer_output/scrappy_2.0_amd64.deb
#           installer_output/Scrappy-2.0-x86_64.AppImage  (if appimagetool found)
#
# Bundled in the package:
#   - Python runtime + all packages  (PyInstaller)
#   - React frontend                 (pre-built static files)
#   - Playwright Chromium            (~130 MB)
#
# System dependencies declared in the .deb (installed by apt on target machine):
#   - libwebkit2gtk-4.0-37 | libwebkit2gtk-4.1-0  (pywebview GTK backend)
#   - libgtk-3-0
#
# Build machine requirements:
#   - Python 3.x + pip
#   - Node.js 18+
#   - python3-gi, gir1.2-webkit2-4.0 (or 4.1)   [for pywebview GTK]
#   - dpkg-deb                                    [usually pre-installed on Ubuntu]
#   - (optional) appimagetool for AppImage output
#
# Author: Soubarna Karmakar
set -euo pipefail

APP_NAME="Scrappy"
APP_VERSION="2.0"
ARCH="amd64"
INSTALL_DIR="/opt/Scrappy"
DEB_NAME="scrappy_${APP_VERSION}_${ARCH}"

echo ""
echo "============================================================"
echo "  Scrappy v${APP_VERSION} -- Linux Build"
echo "  Author: Soubarna Karmakar"
echo "  Output: installer_output/${DEB_NAME}.deb"
echo "============================================================"
echo ""

# ── Pre-flight checks ──────────────────────────────────────────────────────────
command -v python3 >/dev/null 2>&1 || { echo "[ERROR] python3 not found. Install: sudo apt install python3 python3-pip"; exit 1; }
command -v node    >/dev/null 2>&1 || { echo "[ERROR] Node.js not found. Install from https://nodejs.org"; exit 1; }
command -v dpkg-deb >/dev/null 2>&1 || { echo "[ERROR] dpkg-deb not found. Install: sudo apt install dpkg"; exit 1; }

echo "[OK] python3: $(python3 --version)"
echo "[OK] node:    $(node --version)"

# ── Step 1: Python dependencies ────────────────────────────────────────────────
echo ""
echo "[1/6] Installing Python dependencies..."
python3 -m pip install -r requirements.txt --quiet --upgrade
python3 -m pip install pywebview --quiet --upgrade
python3 -m pip install pyinstaller --quiet --upgrade
echo "[OK] Python packages installed."

# ── Step 2: System dependencies for pywebview GTK backend ─────────────────────
echo ""
echo "[2/6] Checking system packages for pywebview GTK backend..."
MISSING_PKGS=()
for pkg in python3-gi python3-gi-cairo gir1.2-webkit2-4.0; do
    dpkg -l "$pkg" >/dev/null 2>&1 || MISSING_PKGS+=("$pkg")
done
# Try webkit2 4.1 if 4.0 not available
if dpkg -l "gir1.2-webkit2-4.1" >/dev/null 2>&1; then
    MISSING_PKGS=("${MISSING_PKGS[@]/gir1.2-webkit2-4.0}")
fi
if [ ${#MISSING_PKGS[@]} -gt 0 ]; then
    echo "  Installing missing system packages: ${MISSING_PKGS[*]}"
    sudo apt-get install -y "${MISSING_PKGS[@]}" 2>/dev/null || \
        echo "  [WARNING] Could not install some packages. pywebview GTK may not work."
else
    echo "  [OK] All GTK/WebKit2 packages present."
fi

# ── Step 3: Build React frontend ──────────────────────────────────────────────
echo ""
echo "[3/6] Building React frontend..."
cd frontend
npm install --silent
npm run build --silent
cd ..
echo "[OK] React build complete."

# ── Step 4: Install Playwright Chromium ───────────────────────────────────────
echo ""
echo "[4/6] Installing Playwright Chromium (Linux)..."
python3 -m playwright install chromium
python3 -m playwright install-deps chromium 2>/dev/null || true
echo "[OK] Playwright Chromium ready."

# ── Step 5: Build with PyInstaller ────────────────────────────────────────────
echo ""
echo "[5/6] Building with PyInstaller..."
echo "      (First run takes 5-10 minutes)"
python3 -m PyInstaller app_linux.spec --clean --noconfirm
echo "[OK] exe built -- dist/Scrappy/"

# ── Step 6: Bundle Playwright Chromium into dist/ ─────────────────────────────
echo ""
echo "[5b] Bundling Playwright Chromium into dist/..."
PW_CACHE="${HOME}/.cache/ms-playwright"
PW_DEST="dist/Scrappy/_playwright_browsers"
mkdir -p "$PW_DEST"
CHROMIUM_FOUND=0
for D in "$PW_CACHE"/chromium-*/; do
    [ -d "$D" ] || continue
    DNAME=$(basename "$D")
    echo "  Copying ${DNAME}..."
    cp -r "$D" "$PW_DEST/$DNAME"
    CHROMIUM_FOUND=1
done
if [ "$CHROMIUM_FOUND" -eq 1 ]; then
    echo "  [OK] Chromium bundled."
else
    echo "  [WARNING] Chromium not found at $PW_CACHE"
    echo "            Run: python3 -m playwright install chromium"
fi

# ── Step 7: Build .deb package ────────────────────────────────────────────────
echo ""
echo "[6/6] Building .deb package..."
mkdir -p installer_output

# Create deb directory structure
DEB_DIR="installer_output/${DEB_NAME}"
rm -rf "$DEB_DIR"
mkdir -p "${DEB_DIR}/DEBIAN"
mkdir -p "${DEB_DIR}${INSTALL_DIR}"
mkdir -p "${DEB_DIR}/usr/share/applications"
mkdir -p "${DEB_DIR}/usr/share/icons/hicolor/256x256/apps"
mkdir -p "${DEB_DIR}/usr/local/bin"

# Copy app files
cp -r dist/Scrappy/. "${DEB_DIR}${INSTALL_DIR}/"
chmod +x "${DEB_DIR}${INSTALL_DIR}/Scrappy"

# Desktop entry
cp assets/scrappy.desktop "${DEB_DIR}/usr/share/applications/scrappy.desktop"

# Icon
if [ -f "assets/icon_1024.png" ]; then
    cp assets/icon_1024.png "${DEB_DIR}/usr/share/icons/hicolor/256x256/apps/scrappy.png"
elif [ -f "assets/icon.png" ]; then
    cp assets/icon.png "${DEB_DIR}/usr/share/icons/hicolor/256x256/apps/scrappy.png"
fi

# Symlink for CLI launch
ln -sf "${INSTALL_DIR}/Scrappy" "${DEB_DIR}/usr/local/bin/scrappy"

# DEBIAN/control
cat > "${DEB_DIR}/DEBIAN/control" << EOF
Package: scrappy
Version: ${APP_VERSION}
Section: utils
Priority: optional
Architecture: ${ARCH}
Depends: libgtk-3-0, libwebkit2gtk-4.0-37 | libwebkit2gtk-4.1-0
Installed-Size: $(du -sk "${DEB_DIR}${INSTALL_DIR}" | cut -f1)
Maintainer: Soubarna Karmakar
Description: Scrappy -- Google Maps Business Scraper
 Scrapes business data from Google Maps with no API key.
 Extracts Name, Address, Phone, Website, Email, Rating, Reviews.
EOF

# DEBIAN/postinst — update icon cache and desktop db
cat > "${DEB_DIR}/DEBIAN/postinst" << 'EOF'
#!/bin/bash
set -e
update-desktop-database /usr/share/applications 2>/dev/null || true
gtk-update-icon-cache /usr/share/icons/hicolor 2>/dev/null || true
chmod +x /opt/Scrappy/Scrappy
EOF
chmod 755 "${DEB_DIR}/DEBIAN/postinst"

# Build the .deb
dpkg-deb --build --root-owner-group "$DEB_DIR" "installer_output/${DEB_NAME}.deb"

echo ""
echo "============================================================"
echo "  .deb package ready:"
echo "    installer_output/${DEB_NAME}.deb"
echo ""
echo "  Install on target Ubuntu machine:"
echo "    sudo dpkg -i ${DEB_NAME}.deb"
echo "    sudo apt-get install -f   # fix any missing deps"
echo "============================================================"

# ── Optional: AppImage ─────────────────────────────────────────────────────────
if command -v appimagetool >/dev/null 2>&1; then
    echo ""
    echo "  Building AppImage..."
    APPDIR="installer_output/Scrappy.AppDir"
    rm -rf "$APPDIR"
    mkdir -p "$APPDIR/usr/bin"
    mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"

    cp -r dist/Scrappy/. "$APPDIR/usr/bin/"
    chmod +x "$APPDIR/usr/bin/Scrappy"

    [ -f "assets/icon.png" ] && cp assets/icon.png "$APPDIR/scrappy.png"
    [ -f "assets/icon.png" ] && cp assets/icon.png "$APPDIR/usr/share/icons/hicolor/256x256/apps/scrappy.png"

    cat > "$APPDIR/AppRun" << 'APPRUN'
#!/bin/bash
exec "$(dirname "$0")/usr/bin/Scrappy" "$@"
APPRUN
    chmod +x "$APPDIR/AppRun"

    cp assets/scrappy.desktop "$APPDIR/scrappy.desktop"
    sed -i 's|Exec=.*|Exec=Scrappy|' "$APPDIR/scrappy.desktop"

    ARCH=x86_64 appimagetool "$APPDIR" "installer_output/Scrappy-${APP_VERSION}-x86_64.AppImage"
    echo "  AppImage ready: installer_output/Scrappy-${APP_VERSION}-x86_64.AppImage"
else
    echo ""
    echo "  [INFO] appimagetool not found -- skipping AppImage."
    echo "         Install: https://appimage.github.io/appimagetool/"
fi

echo ""
echo "Done."
