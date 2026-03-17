#!/usr/bin/env python3
"""
Google Maps Scraper — Desktop Entry Point
Starts the FastAPI server then opens a native pywebview window.
No browser, no Python installation required on end-user machines.

Author    : Soubarna Karmakar
Copyright : © 2025 Soubarna Karmakar. All rights reserved.
Version   : 2.0
"""

__author__    = "Soubarna Karmakar"
__copyright__ = "Copyright © 2025 Soubarna Karmakar. All rights reserved."
__version__   = "2.0"

import socket
import threading
import time
import sys

# ── Find a free port ───────────────────────────────────────────────────────────
def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


PORT = _free_port()
URL  = f"http://127.0.0.1:{PORT}"


# ── Start FastAPI in background thread ────────────────────────────────────────
def _start_server():
    from server import start_server
    start_server(host="127.0.0.1", port=PORT)


server_thread = threading.Thread(target=_start_server, daemon=True)
server_thread.start()


# ── Wait until server is ready ────────────────────────────────────────────────
def _wait_for_server(timeout: float = 15.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", PORT), timeout=1):
                return
        except OSError:
            time.sleep(0.15)
    raise RuntimeError(f"Server did not start within {timeout}s")


_wait_for_server()


# ── Open pywebview native window ──────────────────────────────────────────────
try:
    import webview

    webview.create_window(
        title     = "Google Maps Scraper — by Soubarna Karmakar",
        url       = URL,
        width     = 1280,
        height    = 820,
        min_size  = (1024, 640),
        resizable = True,
        text_select = True,
    )
    webview.start(debug=False)

except ImportError:
    # pywebview not available — fall back to opening system browser
    import webbrowser
    webbrowser.open(URL)
    print(f"\n  Google Maps Scraper is running at {URL}")
    print("  Press Ctrl+C to stop.\n")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sys.exit(0)
