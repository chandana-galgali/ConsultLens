import React from "react";
import type { Trend } from "../types";
import { openDoc } from "../api";

interface Props {
  trends: Trend[];
  fmtDate: (iso: string | null) => string;
}

function changeClass(change: number | null, code: string): string {
  if (change == null) return "change-flat";
  if (code === "bp_sys" || code === "bp" || code === "bp_dia") {
    if (change > 5) return "change-up";
    if (change < -5) return "change-down";
    return "change-flat";
  }
  if (code === "hb") {
    if (change < -0.5) return "change-up";
    if (change > 0.5) return "change-down";
    return "change-flat";
  }
  if (Math.abs(change) < 0.01) return "change-flat";
  return change > 0 ? "change-down" : "change-flat";
}

function changeLabel(change: number | null, code: string, trend: Trend): string {
  if (change == null) return "—";
  // BP: show sys/dia delta
  if (code === "bp" && trend.latest?.dia != null && trend.prev?.dia != null) {
    const dSys = trend.latest.value - trend.prev.value;
    const dDia = trend.latest.dia - trend.prev.dia;
    return `${dSys > 0 ? "+" : ""}${dSys.toFixed(0)}/${dDia > 0 ? "+" : ""}${dDia.toFixed(0)}`;
  }
  const sign = change > 0 ? "+" : "";
  return `${sign}${change.toFixed(1)}`;
}

export default function TrendTable({ trends, fmtDate }: Props) {
  const show = trends.filter((t) => t.latest != null);

  if (show.length === 0) {
    return (
      <div style={{ padding: "16px", color: "var(--fg-3)", fontSize: 13 }}>
        No numeric values extracted yet.
      </div>
    );
  }

  return (
    <table className="trends-table">
      <thead>
        <tr>
          <th>Parameter</th>
          <th>Previous</th>
          <th>Latest</th>
          <th>Δ</th>
        </tr>
      </thead>
      <tbody>
        {show.map((t) => {
          const latestVal = t.code === "bp" && t.latest
            ? t.latest.display ?? `${t.latest.value}/${t.latest.dia}`
            : String(t.latest?.value ?? "—");
          const prevVal = t.code === "bp" && t.prev
            ? t.prev.display ?? `${t.prev.value}/${t.prev.dia}`
            : t.prev ? String(t.prev.value) : null;

          return (
            <tr key={t.code}>
              <td>
                <strong>{t.label}</strong>
                {t.unit && <span style={{ color: "var(--fg-3)", fontSize: 10, marginLeft: 4 }}>{t.unit}</span>}
              </td>
              <td style={{ color: "var(--fg-2)" }}>
                {prevVal ? (
                  <>
                    <span className="val-mono">{prevVal}</span>
                    <span style={{ fontSize: 10, color: "var(--fg-3)", marginLeft: 4 }}>
                      {fmtDate(t.prev?.date ?? null)}
                    </span>
                  </>
                ) : <span style={{ color: "var(--fg-3)" }}>—</span>}
              </td>
              <td>
                <span
                  className="val-mono"
                  style={{ cursor: t.latest?.doc_id ? "pointer" : "default" }}
                  onClick={() => t.latest?.doc_id && openDoc(t.latest.doc_id)}
                  title={t.latest?.doc_id ? "View source document" : undefined}
                >
                  {latestVal}
                </span>
                <span style={{ fontSize: 10, color: "var(--fg-3)", marginLeft: 4 }}>
                  {fmtDate(t.latest?.date ?? null)}
                </span>
              </td>
              <td>
                <span className={changeClass(t.change, t.code)}>
                  {changeLabel(t.change, t.code, t)}
                </span>
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
