import React from "react";
import type { EventT } from "../types";
import { openDoc } from "../api";

interface Props {
  events: EventT[];
  fmtDate: (iso: string | null) => string;
}

const TYPE_COLORS: Record<string, string> = {
  lab: "#0e7490",
  serology: "#7c3aed",
  marker: "#7c3aed",
  usg_nt: "#0891b2",
  usg_level2: "#0891b2",
  usg_growth: "#0891b2",
  usg_doppler: "#0891b2",
  usg_other: "#0891b2",
  vaccine: "#059669",
  visit: "#64748b",
  prescription: "#d97706",
  discharge: "#dc2626",
};

const TYPE_LABELS: Record<string, string> = {
  lab: "Lab",
  serology: "Serology",
  marker: "Marker",
  usg_nt: "NT Scan",
  usg_level2: "Level II",
  usg_growth: "Growth",
  usg_doppler: "Doppler",
  usg_other: "USG",
  vaccine: "Vaccine",
  visit: "Visit",
  prescription: "Rx",
  discharge: "Discharge",
};

function gaFmt(weeks: number | null): string {
  if (weeks == null) return "";
  const w = Math.floor(weeks);
  const d = Math.round((weeks - w) * 7);
  return `${w}+${d}w`;
}

export default function Timeline({ events, fmtDate }: Props) {
  if (events.length === 0) {
    return (
      <div style={{ padding: "40px 20px", textAlign: "center", color: "var(--fg-3)", fontSize: 13 }}>
        No records uploaded yet. Upload documents to see the timeline.
      </div>
    );
  }

  const sorted = [...events].sort((a, b) =>
    (a.date ?? "") < (b.date ?? "") ? 1 : -1
  );

  return (
    <div className="timeline">
      {sorted.map((ev) => {
        const color = TYPE_COLORS[ev.doc_type ?? ""] ?? "#64748b";
        const typeLabel = TYPE_LABELS[ev.doc_type ?? ""] ?? (ev.doc_type ?? "Doc");
        const keyObs = ev.observations.slice(0, 6);
        return (
          <div key={ev.doc_id} className="tl-event">
            <div className="tl-left">
              <div className="tl-dot" style={{ background: color }} />
              <div className="tl-line" />
            </div>
            <div className="tl-content">
              <div className="tl-header">
                <div className="tl-date">{fmtDate(ev.date)}</div>
                <span
                  className="tl-type"
                  style={{ background: color + "22", color, border: `1px solid ${color}44` }}
                >
                  {typeLabel}
                </span>
                {ev.gestation_weeks != null && (
                  <span className="tl-ga">{gaFmt(ev.gestation_weeks)}</span>
                )}
              </div>
              <div className="tl-filename"
                onClick={() => openDoc(ev.doc_id)}
                style={{ cursor: "pointer" }}>
                {ev.original_filename}
                <span style={{ color: "var(--accent)", marginLeft: 6, fontSize: 11 }}>View ↗</span>
              </div>
              {keyObs.length > 0 && (
                <div className="tl-obs">
                  {keyObs.map((o, i) => (
                    <span key={i} className="obs-chip">
                      {o.label}: <strong>{o.value_num ?? o.value_text}</strong>
                      {o.unit && ` ${o.unit}`}
                    </span>
                  ))}
                  {ev.observations.length > 6 && (
                    <span className="obs-chip obs-more">
                      +{ev.observations.length - 6} more
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
