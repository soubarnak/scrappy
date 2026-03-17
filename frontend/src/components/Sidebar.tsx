import React from "react";
import {
  MapPin, Play, Square, Download, Trash2,
  Globe, Mail, Monitor, Phone, ChevronRight,
} from "lucide-react";
import { Button }   from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Switch }   from "@/components/ui/switch";
import { Badge }    from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";

interface Stats {
  total:   number;
  website: number;
  email:   number;
}

interface SidebarProps {
  queries:       string;
  onQueriesChange: (v: string) => void;
  headless:      boolean;
  onHeadlessChange: (v: boolean) => void;
  extractEmails: boolean;
  onExtractEmailsChange: (v: boolean) => void;
  phoneOnly:     boolean;
  onPhoneOnlyChange: (v: boolean) => void;
  isRunning:     boolean;
  onStart:       () => void;
  onStop:        () => void;
  onExport:      () => void;
  onClear:       () => void;
  stats:         Stats;
  canExport:     boolean;
}

export function Sidebar({
  queries, onQueriesChange,
  headless, onHeadlessChange,
  extractEmails, onExtractEmailsChange,
  phoneOnly, onPhoneOnlyChange,
  isRunning, onStart, onStop, onExport, onClear,
  stats, canExport,
}: SidebarProps) {
  return (
    <aside className="flex h-full w-72 shrink-0 flex-col border-r border-border bg-card">

      {/* ── Header ─────────────────────────────────────────────────────── */}
      <div className="gradient-header px-5 py-5">
        <div className="flex items-center gap-3">
          <div className="flex size-10 items-center justify-center rounded-xl bg-primary/20 ring-1 ring-primary/40">
            <MapPin className="size-5 text-primary" />
          </div>
          <div>
            <h1 className="text-base font-bold leading-tight text-foreground">
              Maps Scraper
            </h1>
            <p className="text-[10px] font-medium text-primary/80 tracking-wide uppercase">
              Google Maps Extractor
            </p>
          </div>
        </div>
        <p className="mt-3 text-[11px] text-muted-foreground leading-relaxed">
          by{" "}
          <span className="font-semibold text-primary">Soubarna Karmakar</span>
        </p>
      </div>

      <div className="flex flex-1 flex-col gap-0 overflow-y-auto">

        {/* ── Search Queries ─────────────────────────────────────────────── */}
        <section className="px-4 pt-4 pb-3">
          <label className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            <ChevronRight className="size-3" />
            Search Queries
          </label>
          <Textarea
            value={queries}
            onChange={e => onQueriesChange(e.target.value)}
            placeholder={"IT Companies in Koramangala\nRestaurants in Bandra\nLaw Firms in CP"}
            rows={6}
            className="bg-muted/40 text-sm leading-relaxed font-mono resize-none"
            disabled={isRunning}
          />
          <p className="mt-1.5 text-[10px] text-muted-foreground">
            One query per line — all run sequentially
          </p>
        </section>

        <Separator />

        {/* ── Settings ───────────────────────────────────────────────────── */}
        <section className="px-4 py-3 space-y-3">
          <label className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            <ChevronRight className="size-3" />
            Settings
          </label>

          <ToggleRow
            icon={<Monitor className="size-4 text-muted-foreground" />}
            label="Run in background"
            description="Hide browser window"
            checked={headless}
            onCheckedChange={onHeadlessChange}
            disabled={isRunning}
          />

          <ToggleRow
            icon={<Mail className="size-4 text-muted-foreground" />}
            label="Extract emails"
            description="Visits websites (~8s per place)"
            checked={extractEmails}
            onCheckedChange={onExtractEmailsChange}
            disabled={isRunning}
          />

          <ToggleRow
            icon={<Phone className="size-4 text-muted-foreground" />}
            label="Phone numbers only"
            description="Skip leads without a phone"
            checked={phoneOnly}
            onCheckedChange={onPhoneOnlyChange}
            disabled={isRunning}
          />
        </section>

        <Separator />

        {/* ── Stats ──────────────────────────────────────────────────────── */}
        <section className="px-4 py-3">
          <label className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            <ChevronRight className="size-3" />
            Results
          </label>
          <div className="grid grid-cols-3 gap-2">
            <StatBox label="Found"   value={stats.total}   color="primary" />
            <StatBox label="Website" value={stats.website} color="success" />
            <StatBox label="Email"   value={stats.email}   color="warning" />
          </div>
        </section>

        <Separator />

        {/* ── Action Buttons ─────────────────────────────────────────────── */}
        <section className="px-4 py-4 space-y-2">
          {!isRunning ? (
            <Button
              variant="success"
              className="w-full gap-2 font-semibold"
              onClick={onStart}
              size="lg"
            >
              <Play className="size-4" />
              Start Scraping
            </Button>
          ) : (
            <Button
              variant="destructive"
              className="w-full gap-2 font-semibold animate-pulse-subtle"
              onClick={onStop}
              size="lg"
            >
              <Square className="size-4" />
              Stop
            </Button>
          )}

          <Button
            variant="outline"
            className="w-full gap-2"
            onClick={onExport}
            disabled={!canExport || isRunning}
          >
            <Download className="size-4" />
            Export to Excel
          </Button>

          <Button
            variant="ghost"
            className="w-full gap-2 text-muted-foreground hover:text-destructive"
            onClick={onClear}
            disabled={isRunning || !canExport}
          >
            <Trash2 className="size-4" />
            Clear Results
          </Button>
        </section>
      </div>

      {/* ── Footer ─────────────────────────────────────────────────────── */}
      <div className="border-t border-border px-4 py-3">
        <div className="flex items-center justify-between">
          <span className="text-[10px] text-muted-foreground">v2.0 · No API required</span>
          <Badge variant="muted" className="text-[10px]">
            <Globe className="mr-1 size-2.5" />
            Google Maps
          </Badge>
        </div>
      </div>
    </aside>
  );
}

// ── Sub-components ──────────────────────────────────────────────────────────

function ToggleRow({
  icon, label, description, checked, onCheckedChange, disabled,
}: {
  icon: React.ReactNode;
  label: string;
  description: string;
  checked: boolean;
  onCheckedChange: (v: boolean) => void;
  disabled?: boolean;
}) {
  return (
    <div className={cn(
      "flex items-center justify-between rounded-lg border border-border bg-muted/30 px-3 py-2.5",
      "transition-colors",
      disabled && "opacity-60"
    )}>
      <div className="flex items-center gap-2.5">
        {icon}
        <div>
          <p className="text-sm font-medium leading-none">{label}</p>
          <p className="mt-0.5 text-[10px] text-muted-foreground">{description}</p>
        </div>
      </div>
      <Switch
        checked={checked}
        onCheckedChange={onCheckedChange}
        disabled={disabled}
      />
    </div>
  );
}

function StatBox({
  label, value, color,
}: {
  label: string;
  value: number;
  color: "primary" | "success" | "warning";
}) {
  const colorMap = {
    primary: "text-primary",
    success: "text-success",
    warning: "text-warning",
  };
  return (
    <div className="flex flex-col items-center rounded-lg border border-border bg-muted/30 py-2.5">
      <span className={cn("text-2xl font-bold tabular-nums", colorMap[color])}>
        {value.toLocaleString()}
      </span>
      <span className="mt-0.5 text-[10px] text-muted-foreground">{label}</span>
    </div>
  );
}
