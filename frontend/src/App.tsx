/**
 * Scrappy — Main React App
 * Author    : Soubarna Karmakar
 * Copyright : © 2025 Soubarna Karmakar. All rights reserved.
 * Version   : 2.0
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { Moon, Sun } from "lucide-react";
import { Sidebar }       from "@/components/Sidebar";
import { ResultsTable, type ResultRow } from "@/components/ResultsTable";
import { StatusBar }     from "@/components/StatusBar";
import { Button }        from "@/components/ui/button";

// ── WebSocket URL ─────────────────────────────────────────────────────────────
const WS_URL = `ws://${window.location.host}/ws`;

type Level = "info" | "success" | "warning" | "error";

interface StatusMsg  { message: string; level: Level; }
interface ProgressMsg { current: number; total: number; query: string; }

export default function App() {
  // ── Theme ──────────────────────────────────────────────────────────────────
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", isDark);
  }, [isDark]);

  // ── Settings ──────────────────────────────────────────────────────────────
  const [queries,       setQueries]       = useState("IT Companies in Koramangala\nIT Companies in Whitefield");
  const [headless,      setHeadless]      = useState(false);
  const [extractEmails, setExtractEmails] = useState(false);
  const [phoneOnly,     setPhoneOnly]     = useState(false);
  const [dedup,         setDedup]         = useState(false);

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

          // Deduplication: replace an existing row in-place
          case "result_replace":
            setRows(prev => {
              const next = [...prev];
              if (msg.index >= 0 && msg.index < next.length) {
                next[msg.index] = msg.data as ResultRow;
              }
              return next;
            });
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
              message: "Done! " + msg.total + " results extracted.",
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
    setStatus({ message: "Starting " + queryList.length + " quer" + (queryList.length === 1 ? "y" : "ies") + "…", level: "info" });
    wsRef.current.send(JSON.stringify({
      type: "start",
      queries: queryList,
      options: { headless, extractEmails, phoneOnly, dedup },
    }));
  }, [queries, headless, extractEmails, phoneOnly, dedup]);

  const handleStop = useCallback(() => {
    wsRef.current?.send(JSON.stringify({ type: "stop" }));
    setStatus({ message: "Stop signal sent…", level: "warning" });
  }, []);

  // Export: GET /export — server reads its own result store, no large POST body
  const handleExport = useCallback(async () => {
    if (rows.length === 0) return;
    try {
      const resp = await fetch("/export");
      if (!resp.ok) throw new Error("HTTP " + resp.status);
      const blob = await resp.blob();
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement("a");
      a.href     = url;
      a.download = "scrappy_" + Date.now() + ".xlsx";
      a.click();
      URL.revokeObjectURL(url);
      setStatus({ message: "Exported " + rows.length + " records to Excel.", level: "success" });
    } catch {
      setStatus({ message: "Export failed — check server.", level: "error" });
    }
  }, [rows.length]);

  const handleClear = useCallback(() => {
    setRows([]);
    setProgress({ current: 0, total: 0, query: "" });
    setStatus({ message: "Results cleared. Ready to scrape.", level: "info" });
    // Also clear the server-side store
    wsRef.current?.send(JSON.stringify({ type: "clear" }));
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
        phoneOnly={phoneOnly}
        onPhoneOnlyChange={setPhoneOnly}
        dedup={dedup}
        onDedupChange={setDedup}
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
                : rows.length.toLocaleString() + " places collected"}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <span className="font-semibold text-primary">Soubarna Karmakar</span>
              <span>·</span>
              <span>Scrappy v2.0</span>
            </div>
            {/* Light / Dark toggle */}
            <Button
              variant="ghost"
              size="icon"
              className="size-8"
              onClick={() => setIsDark(d => !d)}
              title={isDark ? "Switch to light mode" : "Switch to dark mode"}
            >
              {isDark
                ? <Sun  className="size-4 text-warning" />
                : <Moon className="size-4 text-primary" />}
            </Button>
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
