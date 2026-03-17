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
import os
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from scraper_engine import ScraperEngine
from email_extractor import EmailExtractor

# ── Resolve the frontend dist folder (works frozen via PyInstaller too) ────────
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).parent

FRONTEND_DIST = BASE_DIR / "frontend" / "dist"

# ── FastAPI app ────────────────────────────────────────────────────────────────
app = FastAPI(title="Google Maps Scraper", version="2.0")

# Active scraper reference (one at a time)
_active_scraper: ScraperEngine | None = None
_scraper_lock   = threading.Lock()


# ── WebSocket endpoint ─────────────────────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    global _active_scraper
    await ws.accept()
    loop = asyncio.get_event_loop()

    async def send(payload: dict):
        """Thread-safe send to WebSocket."""
        try:
            await ws.send_text(json.dumps(payload))
        except Exception:
            pass

    def on_result(data: dict):
        asyncio.run_coroutine_threadsafe(
            send({"type": "result", "data": data}), loop
        )

    def on_status(message: str, level: str = "info"):
        asyncio.run_coroutine_threadsafe(
            send({"type": "status", "message": message, "level": level}), loop
        )

    def on_progress(current: int, total: int, query: str):
        asyncio.run_coroutine_threadsafe(
            send({"type": "progress", "current": current,
                  "total": total, "query": query}), loop
        )

    def on_complete(total: int):
        asyncio.run_coroutine_threadsafe(
            send({"type": "complete", "total": total}), loop
        )

    try:
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)
            kind = msg.get("type")

            # ── START ──────────────────────────────────────────────────────────
            if kind == "start":
                queries = [q.strip() for q in msg.get("queries", []) if q.strip()]
                opts    = msg.get("options", {})
                headless       = bool(opts.get("headless", False))
                extract_emails = bool(opts.get("extractEmails", False))

                if not queries:
                    await send({"type": "status",
                                "message": "No queries provided.", "level": "error"})
                    continue

                with _scraper_lock:
                    if _active_scraper and _active_scraper.is_running:
                        await send({"type": "status",
                                    "message": "Scraper already running.",
                                    "level": "warning"})
                        continue

                    email_ext = EmailExtractor() if extract_emails else None
                    _active_scraper = ScraperEngine(
                        headless=headless,
                        email_extractor=email_ext,
                        on_result=on_result,
                        on_status=on_status,
                        on_progress=on_progress,
                        on_complete=on_complete,
                    )

                # Run in background thread so WebSocket stays responsive
                t = threading.Thread(
                    target=_active_scraper.run,
                    args=(queries,),
                    daemon=True,
                )
                t.start()

            # ── STOP ───────────────────────────────────────────────────────────
            elif kind == "stop":
                with _scraper_lock:
                    if _active_scraper:
                        _active_scraper.stop()
                await send({"type": "status",
                            "message": "Stop signal sent…", "level": "warning"})

            # ── PING ───────────────────────────────────────────────────────────
            elif kind == "ping":
                await send({"type": "pong"})

    except WebSocketDisconnect:
        with _scraper_lock:
            if _active_scraper:
                _active_scraper.stop()
    except Exception as e:
        try:
            await send({"type": "status",
                        "message": f"Server error: {e}", "level": "error"})
        except Exception:
            pass


# ── Serve React build (SPA fallback) ──────────────────────────────────────────
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")),
              name="assets")

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        index = FRONTEND_DIST / "index.html"
        return FileResponse(str(index))
else:
    @app.get("/")
    async def no_frontend():
        return {"error": "Frontend not built. Run: cd frontend && npm run build"}


# ── Excel export endpoint ─────────────────────────────────────────────────────
COLUMNS = ["Name", "Address", "Category", "Phone", "Website", "Email", "Query"]
COL_WIDTHS = {"Name": 28, "Address": 38, "Category": 18,
              "Phone": 16, "Website": 32, "Email": 28, "Query": 22}

class ExportRequest(BaseModel):
    rows: List[dict]

@app.post("/export")
async def export_excel(req: ExportRequest):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Google Maps Data"

    # Header style
    hdr_fill = PatternFill("solid", fgColor="6E56CF")
    hdr_font = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
    hdr_align = Alignment(horizontal="center", vertical="center")
    alt_fill  = PatternFill("solid", fgColor="1E1E3A")
    thin = Border(
        left=Side(style="thin", color="303052"),
        right=Side(style="thin", color="303052"),
        top=Side(style="thin", color="303052"),
        bottom=Side(style="thin", color="303052"),
    )

    for ci, col in enumerate(COLUMNS, 1):
        cell = ws.cell(row=1, column=ci, value=col)
        cell.font  = hdr_font
        cell.fill  = hdr_fill
        cell.alignment = hdr_align
        cell.border = thin
        ws.column_dimensions[get_column_letter(ci)].width = COL_WIDTHS.get(col, 20)

    for ri, row in enumerate(req.rows, 2):
        for ci, col in enumerate(COLUMNS, 1):
            cell = ws.cell(row=ri, column=ci, value=row.get(col, ""))
            cell.border = thin
            cell.alignment = Alignment(vertical="center")
            if ri % 2 == 0:
                cell.fill = alt_fill

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(COLUMNS))}{len(req.rows)+1}"
    ws.row_dimensions[1].height = 22

    # Summary sheet
    ws2 = wb.create_sheet("Summary")
    ws2["A1"] = "Google Maps Scraper — Export Summary"
    ws2["A1"].font = Font(bold=True, size=13)
    ws2["A3"] = "Author";    ws2["B3"] = "Soubarna Karmakar"
    ws2["A4"] = "Generated"; ws2["B4"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ws2["A5"] = "Records";   ws2["B5"] = len(req.rows)
    ws2.column_dimensions["A"].width = 16
    ws2.column_dimensions["B"].width = 30

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    filename = f"google_maps_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ── Run standalone (dev mode) ──────────────────────────────────────────────────
def start_server(host: str = "127.0.0.1", port: int = 7410):
    uvicorn.run(app, host=host, port=port, log_level="error")


if __name__ == "__main__":
    start_server()
