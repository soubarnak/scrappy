#!/usr/bin/env python3
"""
Google Maps Scraper — FastAPI WebSocket Server
Serves the React frontend and handles real-time scraping over WebSocket.

Author    : Soubarna Karmakar
Copyright : © 2025 Soubarna Karmakar. All rights reserved.
Version   : 2.0
"""

__author__    = "Soubarna Karmakar"
__version__   = "2.0"

import asyncio
import io
import json
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional

# ── Third-party (all required, fail loudly here if missing) ──────────────────
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import openpyxl
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter

# NOTE: scraper_engine and email_extractor are imported LAZILY inside the
# WebSocket handler so that a Playwright import error does NOT crash the
# server on startup — the user still sees the UI and a friendly error message.

# ── Resolve frontend dist folder (PyInstaller-safe) ───────────────────────────
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys._MEIPASS)          # type: ignore[attr-defined]
else:
    BASE_DIR = Path(__file__).parent

FRONTEND_DIST = BASE_DIR / "frontend" / "dist"

# ── FastAPI app ────────────────────────────────────────────────────────────────
app = FastAPI(title="Google Maps Scraper", version="2.0")

# One active scraper at a time
_active_scraper: Optional[Any] = None
_scraper_lock   = threading.Lock()


# ── WebSocket endpoint ─────────────────────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    global _active_scraper
    await ws.accept()
    loop = asyncio.get_event_loop()

    # ── helpers ────────────────────────────────────────────────────────────────
    async def send(payload: dict) -> None:
        try:
            await ws.send_text(json.dumps(payload))
        except Exception:
            pass

    def _cb_result(data: dict) -> None:
        asyncio.run_coroutine_threadsafe(
            send({"type": "result", "data": data}), loop)

    def _cb_status(message: str, level: str = "info") -> None:
        asyncio.run_coroutine_threadsafe(
            send({"type": "status", "message": message, "level": level}), loop)

    def _cb_progress(current: int, total: int, query: str) -> None:
        asyncio.run_coroutine_threadsafe(
            send({"type": "progress", "current": current,
                  "total": total, "query": query}), loop)

    def _cb_complete(total: int) -> None:
        asyncio.run_coroutine_threadsafe(
            send({"type": "complete", "total": total}), loop)

    # ── message loop ──────────────────────────────────────────────────────────
    try:
        while True:
            raw  = await ws.receive_text()
            msg  = json.loads(raw)
            kind = msg.get("type")

            # START ────────────────────────────────────────────────────────────
            if kind == "start":
                queries = [q.strip() for q in msg.get("queries", []) if q.strip()]
                opts    = msg.get("options", {})

                if not queries:
                    await send({"type": "status",
                                "message": "No queries provided.", "level": "error"})
                    continue

                # Lazy import — isolated here so a bad install only shows in UI
                try:
                    from scraper_engine import ScraperEngine   # noqa: PLC0415
                    from email_extractor import EmailExtractor  # noqa: PLC0415
                except ImportError as exc:
                    await send({"type": "status",
                                "message": f"Import error: {exc}. Re-run install.bat.",
                                "level": "error"})
                    continue

                with _scraper_lock:
                    if _active_scraper and _active_scraper.is_running:
                        await send({"type": "status",
                                    "message": "Scraper already running.",
                                    "level": "warning"})
                        continue

                    email_ext = (
                        EmailExtractor() if opts.get("extractEmails") else None
                    )
                    _active_scraper = ScraperEngine(
                        headless        = bool(opts.get("headless", False)),
                        phone_only      = bool(opts.get("phoneOnly", False)),
                        email_extractor = email_ext,
                        on_result     = _cb_result,
                        on_status     = _cb_status,
                        on_progress   = _cb_progress,
                        on_complete   = _cb_complete,
                    )

                threading.Thread(
                    target=_active_scraper.run,
                    args=(queries,),
                    daemon=True,
                ).start()

            # STOP ─────────────────────────────────────────────────────────────
            elif kind == "stop":
                with _scraper_lock:
                    if _active_scraper:
                        _active_scraper.stop()
                await send({"type": "status",
                            "message": "Stop signal sent…", "level": "warning"})

            # PING ─────────────────────────────────────────────────────────────
            elif kind == "ping":
                await send({"type": "pong"})

    except WebSocketDisconnect:
        with _scraper_lock:
            if _active_scraper:
                _active_scraper.stop()
    except Exception as exc:
        try:
            await send({"type": "status",
                        "message": f"Server error: {exc}", "level": "error"})
        except Exception:
            pass


# ── Serve React build (SPA fallback) ──────────────────────────────────────────
if FRONTEND_DIST.exists():
    _assets_dir = FRONTEND_DIST / "assets"
    if _assets_dir.exists():
        app.mount("/assets",
                  StaticFiles(directory=str(_assets_dir)),
                  name="assets")

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str) -> FileResponse:
        return FileResponse(str(FRONTEND_DIST / "index.html"))

else:
    @app.get("/")
    async def no_frontend() -> dict:
        return {
            "status": "error",
            "message": "Frontend not built.",
            "fix": "cd frontend && npm install && npm run build",
        }


# ── Excel export ──────────────────────────────────────────────────────────────
_COLS      = ["Name", "Address", "Category", "Phone", "Website", "Email", "Rating", "Reviews", "Query"]
_COL_WIDTH = {"Name": 28, "Address": 38, "Category": 18,
               "Phone": 16, "Website": 32, "Email": 28,
               "Rating": 10, "Reviews": 12, "Query": 22}


class ExportRequest(BaseModel):
    rows: List[dict]


_NUM_COLS    = {"Reviews"}   # stored as int in Excel
_PHONE_COLS  = {"Phone"}     # stored as text with @ format (preserves + and leading zeros)

@app.post("/export")
async def export_excel(req: ExportRequest) -> StreamingResponse:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Scrappy Data"

    hdr_font  = Font(name="Calibri", bold=True, size=11)
    hdr_align = Alignment(horizontal="center", vertical="center")

    for ci, col in enumerate(_COLS, 1):
        cell = ws.cell(row=1, column=ci, value=col)
        cell.font      = hdr_font
        cell.alignment = hdr_align
        ws.column_dimensions[get_column_letter(ci)].width = _COL_WIDTH.get(col, 20)

    for ri, row in enumerate(req.rows, 2):
        for ci, col in enumerate(_COLS, 1):
            raw = row.get(col, "")
            # Store numeric columns as actual numbers so Excel can sort/sum them
            if col in _NUM_COLS and raw:
                try:
                    raw = int(raw)
                except (ValueError, TypeError):
                    pass
            elif col == "Rating" and raw:
                try:
                    raw = float(raw)
                except (ValueError, TypeError):
                    pass
            cell = ws.cell(row=ri, column=ci, value=raw)
            cell.alignment = Alignment(vertical="center")
            if col in _PHONE_COLS:
                cell.number_format = "@"   # text format — keeps +, leading zeros

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(_COLS))}{len(req.rows) + 1}"
    ws.row_dimensions[1].height = 22

    ws2 = wb.create_sheet("Summary")
    ws2["A1"] = "Scrappy — Export Summary"
    ws2["A1"].font = Font(bold=True, size=13)
    ws2["A3"] = "Author";    ws2["B3"] = "Soubarna Karmakar"
    ws2["A4"] = "Generated"; ws2["B4"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ws2["A5"] = "Records";   ws2["B5"] = len(req.rows)
    ws2.column_dimensions["A"].width = 16
    ws2.column_dimensions["B"].width = 30

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="google_maps_{ts}.xlsx"'},
    )


# ── Standalone entry (dev mode: python server.py) ─────────────────────────────
def start_server(host: str = "127.0.0.1", port: int = 7410) -> None:
    uvicorn.run(app, host=host, port=port, log_level="warning")


if __name__ == "__main__":
    start_server()
