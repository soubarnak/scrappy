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


# ── Open pywebview native window (or fallback to browser) ─────────────────────
def _open_browser_fallback() -> None:
    """
    pywebview is unavailable or its EdgeChromium backend failed.
    Show a small tkinter window so the user can see the app is running
    and open it in their browser with one click.
    """
    import webbrowser
    webbrowser.open(URL)

    try:
        import tkinter as tk
        from tkinter import font as tkfont

        root = tk.Tk()
        root.title("Scrappy — by Soubarna Karmakar")
        root.resizable(False, False)
        # Centre on screen
        root.update_idletasks()
        w, h = 380, 180
        x = (root.winfo_screenwidth()  - w) // 2
        y = (root.winfo_screenheight() - h) // 2
        root.geometry(f"{w}x{h}+{x}+{y}")

        bold = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        norm = tkfont.Font(family="Segoe UI", size=9)

        tk.Label(root, text="Scrappy is running", font=bold, pady=12).pack()
        tk.Label(root, text=URL, font=norm, fg="#1a6ed8", cursor="hand2").pack()
        tk.Label(root, text="(opened in your default browser)", font=norm,
                 fg="#666").pack(pady=4)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Open in Browser",
                  command=lambda: webbrowser.open(URL),
                  width=16).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Quit",
                  command=root.destroy,
                  width=10).pack(side="left", padx=6)

        root.mainloop()

    except Exception:
        # tkinter not available — just keep the server alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    sys.exit(0)


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

except ImportError:
    # pywebview not installed — browser fallback
    _open_browser_fallback()

except Exception as exc:
    # edgechromium not available (older Windows / WebView2 not installed)
    # Fall back to browser silently
    print(f"[pywebview error] {exc} — falling back to browser", file=sys.stderr)
    _open_browser_fallback()
