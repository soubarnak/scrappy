import React from "react";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

type Level = "info" | "success" | "warning" | "error";

interface StatusBarProps {
  message:   string;
  level:     Level;
  current:   number;
  total:     number;
  query:     string;
  isRunning: boolean;
}

const levelStyles: Record<Level, string> = {
  info:    "text-muted-foreground",
  success: "text-success",
  warning: "text-warning",
  error:   "text-destructive",
};

const levelDot: Record<Level, string> = {
  info:    "bg-muted-foreground",
  success: "bg-success",
  warning: "bg-warning",
  error:   "bg-destructive",
};

export function StatusBar({
  message, level, current, total, query, isRunning,
}: StatusBarProps) {
  const pct = total > 0 ? Math.round((current / total) * 100) : 0;

  return (
    <footer className="border-t border-border bg-card px-4 py-2">
      {/* Progress bar */}
      <Progress
        value={isRunning && total === 0 ? undefined : pct}
        indeterminate={isRunning && total === 0}
        className="mb-2"
      />

      {/* Status text */}
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-2 min-w-0">
          <span className={cn(
            "inline-block size-1.5 shrink-0 rounded-full",
            isRunning ? "animate-pulse " + levelDot[level] : levelDot[level]
          )} />
          <span className={cn("truncate text-xs", levelStyles[level])}>
            {message || "Ready"}
          </span>
        </div>

        <div className="flex items-center gap-3 shrink-0 text-xs text-muted-foreground">
          {isRunning && total > 0 && (
            <>
              <span className="font-mono tabular-nums">
                {current}/{total}
              </span>
              <span className="text-primary font-semibold">{pct}%</span>
            </>
          )}
          {query && (
            <span className="max-w-[200px] truncate hidden sm:inline" title={query}>
              "{query}"
            </span>
          )}
        </div>
      </div>
    </footer>
  );
}
