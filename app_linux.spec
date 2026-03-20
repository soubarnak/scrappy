# -*- mode: python ; coding: utf-8 -*-
# Scrappy -- PyInstaller spec for Linux (Ubuntu/Debian)
# Author    : Soubarna Karmakar
# Copyright : (c) 2025 Soubarna Karmakar. All rights reserved.

import os
import sys
from pathlib import Path

ROOT = Path(SPECPATH)

from PyInstaller.utils.hooks import collect_all, collect_data_files

pw_datas, pw_bins, pw_hiddens = collect_all("playwright")
wv_datas, wv_bins, wv_hiddens = collect_all("webview")

block_cipher = None

a = Analysis(
    [str(ROOT / "app.py")],
    pathex=[str(ROOT)],
    binaries=[*pw_bins, *wv_bins],
    datas=[
        (str(ROOT / "frontend" / "dist"), "frontend/dist"),
        *pw_datas,
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
        # pywebview -- GTK backend for Linux
        "webview", "webview.platforms.gtk",
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
    console=False,
    icon=str(ROOT / "assets" / "icon.png") if (ROOT / "assets" / "icon.png").exists() else None,
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
