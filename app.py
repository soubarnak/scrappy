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


# ── Auto-install WebView2 then restart ────────────────────────────────────────
def _try_install_webview2_and_restart(exc: Exception | None = None) -> None:
    """
    Called when pywebview cannot find WebView2.
    1. Look for a bundled installer next to the exe (placed there by Inno Setup).
    2. If not found, download the ~1.5 MB bootstrapper from Microsoft.
    3. Run it silently, then restart Scrappy.
    4. If everything fails, show a clear manual-install dialog.
    """
    import os
    import subprocess
    import urllib.request
    import tempfile

    # ── Step 1: Look for bundled installer ────────────────────────────────────
    exe_dir = (
        os.path.dirname(sys.executable)
        if getattr(sys, "frozen", False)
        else os.path.dirname(os.path.abspath(__file__))
    )
    bundled = os.path.join(exe_dir, "MicrosoftEdgeWebView2RuntimeInstallerX64.exe")

    installer_path: str | None = None

    if os.path.isfile(bundled):
        installer_path = bundled
        print("[WebView2] Using bundled installer:", bundled, file=sys.stderr)

    # ── Step 2: Download bootstrapper if no bundled file ──────────────────────
    if installer_path is None:
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            proceed = messagebox.askyesno(
                "Scrappy — Install Required",
                "Microsoft Edge WebView2 is required but not installed.\n\n"
                "Scrappy will now download and install it automatically (~2 MB).\n"
                "An internet connection is needed for this one-time step.\n\n"
                "Click Yes to install now, or No to cancel.",
            )
            root.destroy()
            if not proceed:
                sys.exit(0)
        except Exception:
            pass   # no tkinter — proceed silently

        try:
            print("[WebView2] Downloading bootstrapper...", file=sys.stderr)
            tmp_path = os.path.join(tempfile.gettempdir(), "MicrosoftEdgeWebView2Setup.exe")
            urllib.request.urlretrieve(
                "https://go.microsoft.com/fwlink/p/?LinkId=2124703",
                tmp_path,
            )
            installer_path = tmp_path
            print("[WebView2] Bootstrapper saved to:", tmp_path, file=sys.stderr)
        except Exception as dl_exc:
            print(f"[WebView2] Download failed: {dl_exc}", file=sys.stderr)

    # ── Step 3: Run the installer silently ────────────────────────────────────
    if installer_path and os.path.isfile(installer_path):
        try:
            print("[WebView2] Running installer silently...", file=sys.stderr)
            result = subprocess.run(
                [installer_path, "/silent", "/install"],
                timeout=120,
            )
            print(f"[WebView2] Installer exit code: {result.returncode}", file=sys.stderr)

            if result.returncode == 0:
                # ── Step 4: WebView2 freshly installed — restart ───────────────
                print("[WebView2] Installed. Restarting Scrappy...", file=sys.stderr)
                os.execv(sys.executable, [sys.executable] + sys.argv)
                # execv replaces the current process — code below is unreachable

        if result.returncode == 1603:
                # Already installed — WebView2 is not the problem.
                # pywebview itself is failing (missing DLL, version mismatch, etc.)
                _show_error_and_exit(
                    "WebView2 is installed but could not be used",
                    "Microsoft Edge WebView2 is already installed on this system,\n"
                    "but Scrappy could not open its window.\n\n"
                    "This is usually caused by a pywebview compatibility issue.\n"
                    "Please contact support or report this at:\n"
                    "  github.com/soubarnak/scrappy/issues\n\n"
                    f"Technical detail: {exc}"
                )
                return
        except Exception as run_exc:
            print(f"[WebView2] Installer failed: {run_exc}", file=sys.stderr)

    # ── Step 5: All automatic steps failed — show manual instructions ─────────
    _show_error_and_exit(
        "WebView2 installation failed",
        "Scrappy could not install Microsoft Edge WebView2 automatically.\n\n"
        "Please install it manually:\n"
        "  1. Open Windows Update → Optional Updates, OR\n"
        "  2. Visit: aka.ms/webview2\n\n"
        "After installing, launch Scrappy again.",
    )


# ── Show a native error dialog and exit ───────────────────────────────────────
def _show_webview_error(exc: Exception | None = None) -> None:
    """Called when pywebview/EdgeChromium cannot open."""
    print(f"\n[ERROR] WebView2 not available: {exc}", file=sys.stderr)
    _try_install_webview2_and_restart(exc)


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
