/**
 * Google Maps Scraper — Main React App
 * Author    : Soubarna Karmakar
 * Copyright : © 2025 Soubarna Karmakar. All rights reserved.
 * Version   : 2.0
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { Sidebar }       from "@/components/Sidebar";
import { ResultsTable, type ResultRow } from "@/components/ResultsTable";
import { StatusBar }     from "@/components/StatusBar";

// ── WebSocket URL ─────────────────────────────────────────────────────────────
// In production the server runs on the same host/port as the app.
// In Vite dev mode the proxy in vite.config.ts forwards /ws → localhost:7410
const WS_URL = `ws://${window.location.host}/ws`;

type Level = "info" | "success" | "warning" | "error";

interface StatusMsg { message: string; level: Level; }
interface ProgressMsg { current: number; total: number; query: string; }

export default function App() {
  // ── Settings ─────────────────────────────────────────────────────────────
  const [queries,       setQueries]       = useState("IT Companies in Koramangala\nIT Companies in Whitefield");
  const [headless,      setHeadless]      = useState(false);
  const [extractEmails, setExtractEmails] = useState(false);

  // ── State ─────────────────────────────────────────────────────────────────
  const [isRunning, setIsRunning] = useState(false);
  const [rows,      setRows]      = useState<ResultRow[]>([]);
  const [status,    setStatus]    = useState<StatusMsg>({ message: "Ready to scrape", level: "info" });
  const [progress,  setProgress]  = useState<ProgressMsg>({ current: 0, total: 0, query: "" });

  const wsRef = useRef<WebSocket | null>(null);

  // ── WebSocket lifecycle ───────────────────────────────────────────────────
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      setStatus({ message: "Connected to scraper engine", level: "success" });
    };

    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data as string);

        switch (msg.type) {
          case "result":
            setRows(prev => [...prev, msg.data as ResultRow]);
            break;

          case "status":
            setStatus({ message: msg.message, level: msg.level ?? "info" });
            break;

          case "progress":
            setProgress({ current: msg.current, total: msg.total, query: msg.query });
            break;

          case "complete":
            setIsRunning(false);
            setProgress({ current: 0, total: 0, query: "" });
            setStatus({
              message: `✓ Done! ${msg.total} results extracted.`,
              level: "success",
            });
            break;

          default:
            break;
        }
      } catch {
        /* ignore malformed frames */
      }
    };

    ws.onerror = () => {
      setStatus({ message: "Connection error — retrying…", level: "error" });
    };

    ws.onclose = () => {
      setIsRunning(false);
      // Auto-reconnect after 2 s (server may still be starting up)
      setTimeout(connect, 2000);
    };
  }, []);

  useEffect(() => {
    connect();
    return () => { wsRef.current?.close(); };
  }, [connect]);

  // ── Actions ───────────────────────────────────────────────────────────────
  const handleStart = useCallback(() => {
    const queryList = queries.split("\n").map(q => q.trim()).filter(Boolean);
    if (queryList.length === 0) {
      setStatus({ message: "Please enter at least one query.", level: "warning" });
      return;
    }
    if (wsRef.current?.readyState !== WebSocket.OPEN) {
      setStatus({ message: "Not connected — please wait…", level: "error" });
      return;
    }
    setIsRunning(true);
    setStatus({ message: `Starting ${queryList.length} quer${queryList.length === 1 ? "y" : "ies"}…`, level: "info" });
    wsRef.current.send(JSON.stringify({
      type: "start",
      queries: queryList,
      options: { headless, extractEmails },
    }));
  }, [queries, headless, extractEmails]);

  const handleStop = useCallback(() => {
    wsRef.current?.send(JSON.stringify({ type: "stop" }));
    setStatus({ message: "Stop signal sent…", level: "warning" });
  }, []);

  const handleExport = useCallback(async () => {
    if (rows.length === 0) return;

    // Build xlsx via SheetJS (loaded via CDN) or fall back to requesting
    // the Python backend to write the file via a simple fetch call.
    try {
      const resp = await fetch("/export", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ rows }),
      });
      if (resp.ok) {
        const blob = await resp.blob();
        const url  = URL.createObjectURL(blob);
        const a    = document.createElement("a");
        a.href     = url;
        a.download = `google_maps_scraper_${Date.now()}.xlsx`;
        a.click();
        URL.revokeObjectURL(url);
        setStatus({ message: `Exported ${rows.length} records to Excel.`, level: "success" });
      } else {
        throw new Error("Export failed");
      }
    } catch {
      setStatus({ message: "Export failed — check server.", level: "error" });
    }
  }, [rows]);

  const handleClear = useCallback(() => {
    setRows([]);
    setProgress({ current: 0, total: 0, query: "" });
    setStatus({ message: "Results cleared. Ready to scrape.", level: "info" });
  }, []);

  // ── Stats ─────────────────────────────────────────────────────────────────
  const stats = {
    total:   rows.length,
    website: rows.filter(r => r.Website).length,
    email:   rows.filter(r => r.Email && r.Email !== "N/A").length,
  };

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background">
      {/* Left sidebar */}
      <Sidebar
        queries={queries}
        onQueriesChange={setQueries}
        headless={headless}
        onHeadlessChange={setHeadless}
        extractEmails={extractEmails}
        onExtractEmailsChange={setExtractEmails}
        isRunning={isRunning}
        onStart={handleStart}
        onStop={handleStop}
        onExport={handleExport}
        onClear={handleClear}
        stats={stats}
        canExport={rows.length > 0}
      />

      {/* Main content */}
      <div className="flex flex-1 flex-col min-w-0">
        {/* Header */}
        <header className="flex items-center justify-between border-b border-border bg-card px-5 py-3">
          <div>
            <h2 className="text-sm font-semibold text-foreground">Extracted Data</h2>
            <p className="text-xs text-muted-foreground">
              {rows.length === 0
                ? "Results will appear here in real time"
                : `${rows.length.toLocaleString()} places collected`}
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span className="font-semibold text-primary">Soubarna Karmakar</span>
            <span>·</span>
            <span>Google Maps Scraper v2.0</span>
          </div>
        </header>

        {/* Results table */}
        <div className="flex-1 overflow-hidden">
          <ResultsTable rows={rows} isRunning={isRunning} />
        </div>

        {/* Status bar */}
        <StatusBar
          message={status.message}
          level={status.level}
          current={progress.current}
          total={progress.total}
          query={progress.query}
          isRunning={isRunning}
        />
      </div>
    </div>
  );
}
