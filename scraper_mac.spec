# -*- mode: python ; coding: utf-8 -*-
# ─────────────────────────────────────────────────────────────────────────────
# Google Maps Scraper — PyInstaller spec  (macOS)
# Author:  Soubarna Karmakar  |  Copyright © 2025. All rights reserved.
# Build:   pyinstaller scraper_mac.spec --clean --noconfirm
# ─────────────────────────────────────────────────────────────────────────────

from PyInstaller.utils.hooks import collect_all, collect_data_files

# ── Collect all assets & hidden imports from key packages ────────────────────
d_ctk,  b_ctk,  h_ctk  = collect_all('customtkinter')
d_pw,   b_pw,   h_pw   = collect_all('playwright')
d_oxl                  = collect_data_files('openpyxl')
d_bs4                  = collect_data_files('bs4')
d_cert                 = collect_data_files('certifi')

ALL_DATAS   = d_ctk + d_pw + d_oxl + d_bs4 + d_cert
ALL_BINS    = b_ctk + b_pw
ALL_HIDDEN  = h_ctk + h_pw + [
    'tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox',
    '_tkinter',
    'openpyxl', 'openpyxl.styles', 'openpyxl.utils',
    'requests', 'urllib3', 'certifi', 'idna', 'charset_normalizer',
    'bs4', 'html.parser',
    'pandas',
    'playwright', 'playwright.sync_api', 'playwright._impl',
    'playwright._impl._driver',
]

a = Analysis(
    ['scraper.py'],
    pathex=[],
    binaries=ALL_BINS,
    datas=ALL_DATAS,
    hiddenimports=ALL_HIDDEN,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'numpy', 'scipy', 'IPython', 'jupyter',
        'PyQt5', 'PyQt6', 'PySide2', 'PySide6', 'wx',
        'test', 'unittest', 'doctest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GoogleMapsScraper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,           # UPX often causes issues on macOS — keep off
    upx_exclude=[],
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,   # macOS: allow opening files by drag-and-drop
    target_arch=None,      # Set to 'x86_64' or 'arm64' for single-arch builds
    codesign_identity=None,
    entitlements_file=None,
    # icon='assets/icon.icns',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='GoogleMapsScraper',
)

app = BUNDLE(
    coll,
    name='GoogleMapsScraper.app',
    # icon='assets/icon.icns',   # uncomment after running create_icon.py on macOS
    bundle_identifier='com.googlemapsscraper.app',
    info_plist={
        'CFBundleName':              'Google Maps Scraper',
        'CFBundleDisplayName':       'Google Maps Scraper',
        'CFBundleShortVersionString': '2.0',
        'CFBundleVersion':           '2.0',
        'NSHighResolutionCapable':   True,
        'NSPrincipalClass':          'NSApplication',
        # Required on macOS 10.14+ for automation
        'NSAppleEventsUsageDescription': 'Used for browser automation.',
        # Allow running without signing (Gatekeeper note in README)
        'LSMinimumSystemVersion':    '10.14',
    },
)
