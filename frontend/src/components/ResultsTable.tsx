import React, { useState, useMemo, useCallback } from "react";
import {
  ArrowUpDown, ArrowUp, ArrowDown,
  Copy, ExternalLink, Phone, Mail, MapPin, Tag,
} from "lucide-react";
import { Input }  from "@/components/ui/input";
import { Badge }  from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export interface ResultRow {
  Name:     string;
  Address:  string;
  Category: string;
  Phone:    string;
  Website:  string;
  Email:    string;
  Query:    string;
}

type SortDir = "asc" | "desc" | null;
type Col     = keyof ResultRow;

interface ResultsTableProps {
  rows: ResultRow[];
  isRunning: boolean;
}

const COLS: { key: Col; label: string; icon: React.ReactNode; width: string }[] = [
  { key: "Name",     label: "Name",     icon: <MapPin className="size-3" />,     width: "min-w-[180px] max-w-[220px]" },
  { key: "Address",  label: "Address",  icon: <MapPin className="size-3" />,     width: "min-w-[200px] max-w-[280px]" },
  { key: "Category", label: "Category", icon: <Tag    className="size-3" />,     width: "min-w-[120px] max-w-[160px]" },
  { key: "Phone",    label: "Phone",    icon: <Phone  className="size-3" />,     width: "min-w-[130px] max-w-[160px]" },
  { key: "Website",  label: "Website",  icon: <ExternalLink className="size-3" />, width: "min-w-[160px] max-w-[220px]" },
  { key: "Email",    label: "Email",    icon: <Mail   className="size-3" />,     width: "min-w-[160px] max-w-[220px]" },
  { key: "Query",    label: "Query",    icon: <Tag    className="size-3" />,     width: "min-w-[140px] max-w-[180px]" },
];

export function ResultsTable({ rows, isRunning }: ResultsTableProps) {
  const [filter,  setFilter]  = useState("");
  const [sortCol, setSortCol] = useState<Col | null>(null);
  const [sortDir, setSortDir] = useState<SortDir>(null);
  const [copied,  setCopied]  = useState<string | null>(null);

  // Filter
  const filtered = useMemo(() => {
    if (!filter.trim()) return rows;
    const q = filter.toLowerCase();
    return rows.filter(r =>
      Object.values(r).some(v => v.toLowerCase().includes(q))
    );
  }, [rows, filter]);

  // Sort
  const sorted = useMemo(() => {
    if (!sortCol || !sortDir) return filtered;
    return [...filtered].sort((a, b) => {
      const av = a[sortCol].toLowerCase();
      const bv = b[sortCol].toLowerCase();
      return sortDir === "asc"
        ? av.localeCompare(bv)
        : bv.localeCompare(av);
    });
  }, [filtered, sortCol, sortDir]);

  const handleSort = useCallback((col: Col) => {
    if (sortCol !== col) { setSortCol(col); setSortDir("asc"); return; }
    if (sortDir === "asc")  { setSortDir("desc"); return; }
    if (sortDir === "desc") { setSortCol(null); setSortDir(null); }
  }, [sortCol, sortDir]);

  const copyCell = useCallback((text: string, id: string) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(id);
      setTimeout(() => setCopied(null), 1500);
    });
  }, []);

  const exportCSV = useCallback(() => {
    const header = COLS.map(c => c.label).join(",");
    const body   = rows.map(r =>
      COLS.map(c => `"${(r[c.key] || "").replace(/"/g, '""')}"`).join(",")
    ).join("\n");
    const blob = new Blob([header + "\n" + body], { type: "text/csv" });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href     = url;
    a.download = `maps_scraper_${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }, [rows]);

  return (
    <div className="flex h-full flex-col">

      {/* ── Toolbar ──────────────────────────────────────────────────────── */}
      <div className="flex items-center gap-3 border-b border-border bg-card px-4 py-2.5">
        <Input
          value={filter}
          onChange={e => setFilter(e.target.value)}
          placeholder="Filter results…"
          className="h-8 max-w-xs text-sm bg-muted/40"
        />
        <div className="flex items-center gap-1.5 ml-auto">
          {isRunning && (
            <Badge variant="warning" className="animate-pulse-subtle">
              <span className="mr-1.5 inline-block size-1.5 rounded-full bg-warning" />
              Scraping…
            </Badge>
          )}
          <Badge variant="muted">{sorted.length.toLocaleString()} rows</Badge>
          {rows.length > 0 && (
            <Button variant="ghost" size="sm" className="h-7 text-xs" onClick={exportCSV}>
              CSV
            </Button>
          )}
        </div>
      </div>

      {/* ── Table ────────────────────────────────────────────────────────── */}
      <div className="flex-1 overflow-auto selectable">
        <table className="w-full border-collapse text-sm">
          {/* Head */}
          <thead className="sticky top-0 z-10 bg-muted/80 backdrop-blur-sm">
            <tr>
              <th className="w-12 border-b border-border px-3 py-2.5 text-center text-xs text-muted-foreground font-normal">
                #
              </th>
              {COLS.map(col => {
                const isActive = sortCol === col.key;
                return (
                  <th
                    key={col.key}
                    className={cn(
                      "border-b border-border px-3 py-2.5 text-left text-xs font-semibold",
                      "cursor-pointer select-none whitespace-nowrap",
                      "hover:bg-accent/50 transition-colors",
                      col.width,
                      isActive && "text-primary"
                    )}
                    onClick={() => handleSort(col.key)}
                  >
                    <span className="flex items-center gap-1.5">
                      {col.icon}
                      {col.label}
                      {isActive ? (
                        sortDir === "asc"
                          ? <ArrowUp   className="size-3" />
                          : <ArrowDown className="size-3" />
                      ) : (
                        <ArrowUpDown className="size-3 opacity-30" />
                      )}
                    </span>
                  </th>
                );
              })}
            </tr>
          </thead>

          {/* Body */}
          <tbody>
            {sorted.length === 0 ? (
              <tr>
                <td
                  colSpan={COLS.length + 1}
                  className="py-20 text-center text-muted-foreground"
                >
                  {rows.length === 0
                    ? isRunning
                      ? "Collecting results…"
                      : "Enter queries and click Start Scraping"
                    : "No results match your filter"}
                </td>
              </tr>
            ) : (
              sorted.map((row, i) => (
                <TableRow
                  key={i}
                  row={row}
                  index={i}
                  copied={copied}
                  onCopy={copyCell}
                />
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ── Single row ───────────────────────────────────────────────────────────────
function TableRow({
  row, index, copied, onCopy,
}: {
  row:    ResultRow;
  index:  number;
  copied: string | null;
  onCopy: (text: string, id: string) => void;
}) {
  return (
    <tr
      className={cn(
        "group border-b border-border/50 transition-colors animate-slide-in",
        index % 2 === 0 ? "bg-background" : "bg-muted/10",
        "hover:bg-accent/30"
      )}
    >
      {/* Row number */}
      <td className="px-3 py-2 text-center text-xs text-muted-foreground tabular-nums">
        {index + 1}
      </td>

      {/* Name */}
      <Cell id={`${index}-Name`} text={row.Name} copied={copied} onCopy={onCopy}>
        <span className="font-medium text-foreground truncate block max-w-[200px]" title={row.Name}>
          {row.Name || "—"}
        </span>
      </Cell>

      {/* Address */}
      <Cell id={`${index}-Address`} text={row.Address} copied={copied} onCopy={onCopy}>
        <span className="text-muted-foreground truncate block max-w-[260px] text-xs" title={row.Address}>
          {row.Address || "—"}
        </span>
      </Cell>

      {/* Category */}
      <Cell id={`${index}-Category`} text={row.Category} copied={copied} onCopy={onCopy}>
        {row.Category ? (
          <Badge variant="secondary" className="text-[10px]">{row.Category}</Badge>
        ) : <span className="text-muted-foreground">—</span>}
      </Cell>

      {/* Phone */}
      <Cell id={`${index}-Phone`} text={row.Phone} copied={copied} onCopy={onCopy}>
        {row.Phone ? (
          <span className="font-mono text-xs text-foreground">{row.Phone}</span>
        ) : <span className="text-muted-foreground">—</span>}
      </Cell>

      {/* Website */}
      <Cell id={`${index}-Website`} text={row.Website} copied={copied} onCopy={onCopy}>
        {row.Website ? (
          <a
            href={row.Website}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-primary hover:underline truncate max-w-[200px] text-xs"
            title={row.Website}
            onClick={e => e.stopPropagation()}
          >
            <ExternalLink className="size-3 shrink-0" />
            {row.Website.replace(/^https?:\/\//, "").replace(/\/$/, "").slice(0, 30)}
          </a>
        ) : <span className="text-muted-foreground">—</span>}
      </Cell>

      {/* Email */}
      <Cell id={`${index}-Email`} text={row.Email} copied={copied} onCopy={onCopy}>
        {row.Email && row.Email !== "N/A" ? (
          <span className="text-xs text-success">{row.Email}</span>
        ) : <span className="text-muted-foreground text-xs">N/A</span>}
      </Cell>

      {/* Query */}
      <Cell id={`${index}-Query`} text={row.Query} copied={copied} onCopy={onCopy}>
        <span className="truncate block max-w-[160px] text-xs text-muted-foreground" title={row.Query}>
          {row.Query || "—"}
        </span>
      </Cell>
    </tr>
  );
}

// ── Copyable cell ────────────────────────────────────────────────────────────
function Cell({
  id, text, copied, onCopy, children,
}: {
  id:       string;
  text:     string;
  copied:   string | null;
  onCopy:   (text: string, id: string) => void;
  children: React.ReactNode;
}) {
  const isCopied = copied === id;
  return (
    <td className="relative px-3 py-2 group/cell">
      {children}
      {text && (
        <button
          onClick={() => onCopy(text, id)}
          className={cn(
            "absolute right-1.5 top-1/2 -translate-y-1/2 rounded p-0.5",
            "opacity-0 group-hover/cell:opacity-100 transition-opacity",
            "hover:bg-muted",
            isCopied && "opacity-100 text-success"
          )}
          title="Copy"
        >
          <Copy className="size-3" />
        </button>
      )}
    </td>
  );
}
