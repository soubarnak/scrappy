# -*- mode: python ; coding: utf-8 -*-
# Google Maps Scraper — PyInstaller spec (Windows + macOS)
# Author    : Soubarna Karmakar
# Copyright : © 2025 Soubarna Karmakar. All rights reserved.

import os
import sys
from pathlib import Path

ROOT = Path(SPECPATH)

# ── Collect playwright browsers ───────────────────────────────────────────────
from PyInstaller.utils.hooks import collect_all, collect_data_files

pw_datas,  pw_bins,  pw_hiddens  = collect_all("playwright")
wv_datas,  wv_bins,  wv_hiddens  = collect_all("webview")

block_cipher = None

a = Analysis(
    [str(ROOT / "app.py")],
    pathex=[str(ROOT)],
    binaries=[*pw_bins, *wv_bins],
    datas=[
        # React build output → bundled as-is, served by FastAPI StaticFiles
        (str(ROOT / "frontend" / "dist"), "frontend/dist"),
        # Playwright data files (browsers, driver)
        *pw_datas,
        # pywebview data files (JS bridges, icons, etc.)
        *wv_datas,
    ],
    hiddenimports=[
        # FastAPI / Starlette
        "fastapi", "uvicorn", "uvicorn.logging", "uvicorn.loops",
        "uvicorn.loops.auto", "uvicorn.protocols", "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto", "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto", "uvicorn.lifespan",
        "uvicorn.lifespan.on", "starlette", "starlette.staticfiles",
        "starlette.responses", "pydantic",
        # pywebview — collect_all handles platform modules; list key ones explicitly
        "webview", "webview.platforms.edgechromium",
        "webview.platforms.mshtml", "webview.platforms.winforms",
        *wv_hiddens,
        # Playwright
        "playwright", "playwright.sync_api", *pw_hiddens,
        # openpyxl
        "openpyxl", "openpyxl.styles",
        # Email libs
        "requests", "bs4", "lxml",
        # App modules
        "server", "scraper_engine", "email_extractor",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=["customtkinter", "PyQt5", "PyQt6", "wx"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Scrappy",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,           # No console window
    icon=str(ROOT / "assets" / "icon.ico") if (ROOT / "assets" / "icon.ico").exists() else None,
    version_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Scrappy",
)
