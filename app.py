#!/usr/bin/env python3
"""
Google Maps Scraper — Desktop Entry Point
Starts the FastAPI server then opens a native pywebview window.
No Python installation required on end-user machines (PyInstaller exe).

Author    : Soubarna Karmakar
Copyright : © 2025 Soubarna Karmakar. All rights reserved.
Version   : 2.0
"""

__author__    = "Soubarna Karmakar"
__copyright__ = "Copyright © 2025 Soubarna Karmakar. All rights reserved."
__version__   = "2.0"

import socket
import sys
import threading
import time
import traceback

# ── Find a free port ───────────────────────────────────────────────────────────
def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


PORT = _free_port()
URL  = f"http://127.0.0.1:{PORT}"

# Shared slot for exceptions from the server thread
_server_error: Exception | None = None


# ── Start FastAPI in a daemon thread ─────────────────────────────────────────
def _start_server() -> None:
    global _server_error
    try:
        from server import start_server          # lazy — catches import errors
        start_server(host="127.0.0.1", port=PORT)
    except Exception as exc:
        _server_error = exc
        print(f"\n[SERVER CRASHED] {type(exc).__name__}: {exc}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)


server_thread = threading.Thread(target=_start_server, daemon=True)
server_thread.start()


# ── Wait until the server accepts connections ─────────────────────────────────
def _wait_for_server(timeout: float = 20.0) -> None:
    """
    Poll localhost:PORT until the server is ready.
    If the server thread crashes first, raise with the real error message.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        # Check whether the server thread died
        if _server_error is not None:
            _show_error_and_exit(
                "Server failed to start",
                f"{type(_server_error).__name__}: {_server_error}\n\n"
                "Common fixes:\n"
                "  1. Re-run install.bat\n"
                "  2. pip install -r requirements.txt\n"
                "  3. python -m playwright install chromium"
            )

        try:
            with socket.create_connection(("127.0.0.1", PORT), timeout=1):
                return          # server is up
        except OSError:
            time.sleep(0.2)

    _show_error_and_exit(
        "Server timed out",
        f"Server did not respond within {timeout}s.\n\n"
        "Common fixes:\n"
        "  1. Re-run install.bat\n"
        "  2. pip install -r requirements.txt"
    )


def _show_error_and_exit(title: str, message: str) -> None:
    """Show a user-friendly error dialog then exit."""
    print(f"\n[ERROR] {title}: {message}", file=sys.stderr)

    # Try a native dialog first
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            f"Scrappy — {title}",
            message,
        )
        root.destroy()
    except Exception:
        pass  # tkinter might not be available in frozen builds

    sys.exit(1)


_wait_for_server()


# ── Show a native error dialog and exit ───────────────────────────────────────
def _show_webview_error(exc: Exception | None = None) -> None:
    """
    Called when pywebview/EdgeChromium cannot open.  Shows a clear, actionable
    error dialog — no browser fallback.
    """
    detail = f"\n\nTechnical detail:\n{exc}" if exc else ""
    message = (
        "Scrappy requires Microsoft Edge WebView2 to display its window.\n\n"
        "How to fix:\n"
        "  1. Open Windows Update → Optional Updates and install any Edge updates, OR\n"
        "  2. Download and run the WebView2 installer:\n"
        "     go.microsoft.com/fwlink/p/?LinkId=2124703\n\n"
        "After installing WebView2, launch Scrappy again."
        + detail
    )
    print(f"\n[ERROR] WebView2 not available: {exc}", file=sys.stderr)
    _show_error_and_exit("Window could not open", message)


# ── Launch native pywebview window ────────────────────────────────────────────
try:
    import webview                               # type: ignore[import]

    webview.create_window(
        title       = "Scrappy — by Soubarna Karmakar",
        url         = URL,
        width       = 1280,
        height      = 820,
        min_size    = (1024, 640),
        resizable   = True,
        text_select = True,
    )
    # gui='edgechromium' uses Microsoft Edge WebView2 (built into Windows 10/11).
    # This does NOT require pythonnet or .NET SDK — works on Python 3.14+.
    webview.start(gui="edgechromium", debug=False)

except ImportError as exc:
    _show_webview_error(exc)

except Exception as exc:
    _show_webview_error(exc)
