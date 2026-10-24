import React from "react";
import type { GapItem, QualityFlag } from "../types";

interface Props {
  gaps: GapItem[];
  qualityFlags: QualityFlag[];
}

const STATUS_LABEL: Record<string, string> = {
  found: "Done",
  not_found: "Not found",
  window_open: "Due now",
  no_lmp: "Need LMP",
  future: "Upcoming",
};

export default function GapPanel({ gaps, qualityFlags }: Props) {
  const sorted = [...gaps].sort((a, b) => {
    const order = { not_found: 0, window_open: 1, found: 3, future: 4, no_lmp: 2 };
    return (order[a.status] ?? 9) - (order[b.status] ?? 9);
  });

  const conflicts = qualityFlags.filter((f) => f.kind === "conflict");

  if (sorted.length === 0 && conflicts.length === 0) {
    return (
      <div style={{ padding: "16px", color: "var(--fg-3)", fontSize: 13 }}>
        No gaps detected yet. Upload records to check for missing investigations.
      </div>
    );
  }

  return (
    <div>
      {conflicts.map((f, i) => (
        <div key={i} className="gap-item">
          <div className="gap-dot dot-conflict" />
          <div>
            <div className="gap-label">⚠ Conflicting data</div>
            <div className="gap-sub">{f.message}</div>
          </div>
          <div className="gap-right">
            <span className="gap-status status-conflict">Conflict</span>
          </div>
        </div>
      ))}
      {sorted.map((g) => (
        <div key={g.id} className="gap-item">
          <div className={`gap-dot dot-${g.status === "found" ? "ok" : g.status === "window_open" ? "warn" : g.status === "not_found" ? "info" : "grey"}`} />
          <div>
            <div className="gap-label">{g.label}</div>
            <div className="gap-sub">
              {g.status === "found" && g.found_on && `Found · ${g.found_on}${g.found_ga_weeks != null ? ` · GA ${Math.floor(g.found_ga_weeks)}w` : ""}`}
              {g.status === "not_found" && "Not found in uploaded records"}
              {g.status === "window_open" && g.window_weeks && `Expected ${g.window_weeks[0]}–${g.window_weeks[1]} weeks`}
              {g.status === "future" && g.window_weeks && `Expected at ${g.window_weeks[0]}–${g.window_weeks[1]} weeks`}
              {g.status === "no_lmp" && "LMP not recorded — cannot calculate window"}
            </div>
          </div>
          <div className="gap-right">
            <span className={`gap-status status-${g.status}`}>{STATUS_LABEL[g.status] ?? g.status}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
