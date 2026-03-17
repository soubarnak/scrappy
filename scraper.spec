# -*- mode: python ; coding: utf-8 -*-
# ─────────────────────────────────────────────────────────────────────────────
# Google Maps Scraper — PyInstaller spec  (WINDOWS)
# Author:  Soubarna Karmakar  |  Copyright © 2025. All rights reserved.
# Build:   pyinstaller scraper.spec --clean --noconfirm
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
    'tkinter.simpledialog', 'tkinter.colorchooser',
    '_tkinter',
    'openpyxl', 'openpyxl.styles', 'openpyxl.utils',
    'requests', 'urllib3', 'certifi', 'idna', 'charset_normalizer',
    'bs4', 'html.parser', 'lxml',
    'pandas',
    'PIL', 'PIL.Image',
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
    # Trim packages we don't use to keep the bundle smaller
    excludes=[
        'matplotlib', 'numpy', 'scipy', 'IPython', 'jupyter',
        'PyQt5', 'PyQt6', 'PySide2', 'PySide6',
        'wx', 'gi', 'Gtk',
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
    upx=True,
    upx_exclude=[],
    console=False,            # No console window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GoogleMapsScraper',
)
