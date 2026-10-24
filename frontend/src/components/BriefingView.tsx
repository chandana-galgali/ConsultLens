import React, { useState } from "react";
import type { Briefing } from "../types";
import GapPanel from "./GapPanel";
import TrendTable from "./TrendTable";
import Timeline from "./Timeline";

// ── Tab definitions ───────────────────────────────────────────────────────────
const TABS = [
  { id: "overview",        label: "Overview" },
  { id: "investigations",  label: "Investigations" },
  { id: "vitals",          label: "Vitals & BP" },
  { id: "scans",           label: "Scans & USG" },
  { id: "immuno",          label: "Immunisation & Rx" },
  { id: "journey",         label: "Patient Journey" },
  { id: "documents",       label: "Documents" },
];

// ── Helpers ───────────────────────────────────────────────────────────────────
function gaFmt(weeks: number | null): string {
  if (weeks == null) return "GA —";
  const w = Math.floor(weeks);
  const d = Math.round((weeks - w) * 7);
  return `GA ${w}+${d}`;
}

function fmtDateShort(iso: string | null): string {
  if (!iso) return "—";
  const [, m, d] = iso.split("-");
  const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  return `${parseInt(d)} ${months[parseInt(m)-1]}`;
}

function docTypeLabel(t: string | null): string {
  const MAP: Record<string, string> = {
    lab: "Lab Report", usg_nt: "NT Scan", usg_level2: "Level II Scan",
    usg_growth: "Growth Scan", usg_doppler: "Doppler Scan", usg_other: "USG",
    marker: "Serum Marker", vaccine: "Vaccine", visit: "ANC Visit",
    prescription: "Prescription", discharge: "Discharge", serology: "Serology",
  };
  return MAP[t ?? ""] ?? t ?? "Document";
}

function docTypeIcon(t: string | null): { icon: string; cls: string } {
  if (!t) return { icon: "📄", cls: "doc-icon-visit" };
  if (t.startsWith("usg")) return { icon: "🔊", cls: "doc-icon-usg" };
  if (t === "lab" || t === "serology" || t === "marker") return { icon: "🧪", cls: "doc-icon-lab" };
  if (t === "vaccine") return { icon: "💉", cls: "doc-icon-vacc" };
  return { icon: "📋", cls: "doc-icon-visit" };
}

// ── BriefingView ─────────────────────────────────────────────────────────────
interface Props {
  briefing: Briefing;
  onUpload: () => void;
  onRefresh: () => void;
  fmtDate: (iso: string | null) => string;
}

export default function BriefingView({ briefing, onUpload, onRefresh, fmtDate }: Props) {
  const [activeTab, setActiveTab] = useState("overview");
  const { patient: pt, ga_label, edd, summary, summary_source,
          events, trends, gaps, quality_flags, document_count } = briefing;

  const attentionCount = gaps.filter((g) => g.status === "not_found" || g.status === "window_open").length;
  const conflictCount = quality_flags.filter((f) => f.kind === "conflict").length;

  // ── Derived data for sections ─────────────────────────────────────────────

  // Vitals: BP readings from observations across events
  const bpReadings = events
    .map((ev) => {
      const sys = ev.observations.find((o) => o.code === "bp_sys");
      const dia = ev.observations.find((o) => o.code === "bp_dia");
      if (!sys || !dia) return null;
      return {
        date: fmtDateShort(ev.date),
        ga: gaFmt(ev.gestation_weeks),
        sys: sys.value_num ?? 0,
        dia: dia.value_num ?? 0,
      };
    })
    .filter(Boolean) as { date: string; ga: string; sys: number; dia: number }[];

  // Labs: all numeric observations across all events, grouped by code
  const labCodes = ["hb", "tlc", "platelets", "fbs", "ppbs", "hba1c", "tsh", "creatinine", "sgpt", "sgot"];
  const labRows = labCodes
    .map((code) => {
      const obsList = events
        .flatMap((ev) => ev.observations.filter((o) => o.code === code))
        .sort((a, b) => (a.observed_on ?? "") < (b.observed_on ?? "") ? -1 : 1);
      if (!obsList.length) return null;
      return { code, obsList };
    })
    .filter(Boolean) as { code: string; obsList: typeof briefing.trends[0]["points"] extends infer P ? any[] : any[] }[];

  // Serology text observations
  const serologyCodes = ["hiv", "hbsag", "hcv", "vdrl", "blood_group"];
  const serologyRows = serologyCodes
    .map((code) => {
      const obs = events
        .flatMap((ev) => ev.observations.filter((o) => o.code === code))
        .sort((a, b) => (a.observed_on ?? "") > (b.observed_on ?? "") ? -1 : 1)[0];
      return obs ? { code, obs } : null;
    })
    .filter(Boolean) as { code: string; obs: any }[];

  // Vaccines
  const vaccCodes = ["tt1", "tt2", "tt_booster", "influenza"];
  const vaccRows = vaccCodes
    .map((code) => {
      const obs = events.flatMap((ev) => ev.observations.filter((o) => o.code === code))[0];
      return obs ? { code, obs } : null;
    })
    .filter(Boolean) as { code: string; obs: any }[];

  // Medications
  const medObs = events
    .flatMap((ev) => ev.observations.filter((o) => o.code === "medication"))
    .sort((a, b) => (a.observed_on ?? "") > (b.observed_on ?? "") ? -1 : 1);

  // Scan events
  const scanEvents = events.filter((ev) =>
    ev.doc_type?.startsWith("usg") || ev.doc_type === "marker"
  );

  // Weight
  const weightTrend = trends.find((t) => t.code === "weight" || t.code === "wt");

  return (
    <>
      {/* ── Topbar ──────────────────────────────────────────────────────── */}
      <div className="topbar">
        <div className="topbar-patient">
          <div className="pt-name">{pt.name}</div>
          <div className="pt-subline">
            {pt.age && <span>{pt.age} yrs</span>}
            {pt.age && pt.lmp && <span className="sep">·</span>}
            {pt.lmp && <span>LMP {fmtDate(pt.lmp)}</span>}
            {pt.lmp && edd && <span className="sep">·</span>}
            {edd && <span>EDD {fmtDate(edd)}</span>}
          </div>
        </div>
        <div className="topbar-actions">
          <div className="ga-pill">{ga_label}</div>
          <button className="btn btn-outline" onClick={onUpload}>⬆ Upload Records</button>
          <button className="btn btn-ghost" onClick={onRefresh} title="Refresh briefing">↻</button>
        </div>
      </div>

      {/* ── Tabs ────────────────────────────────────────────────────────── */}
      <div className="tabs">
        {TABS.map((tab) => (
          <div
            key={tab.id}
            className={`tab${activeTab === tab.id ? " active" : ""}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
            {tab.id === "overview" && attentionCount > 0 && (
              <span className="tab-badge">{attentionCount}</span>
            )}
          </div>
        ))}
      </div>

      {/* ── Content ─────────────────────────────────────────────────────── */}
      <div className="content fade-in">

        {/* OVERVIEW ──────────────────────────────────────────────────────── */}
        {activeTab === "overview" && (
          <>
            <div className="summary-banner">
              <div className="label">Pre-consultation Summary</div>
              <p>{summary || "No summary available yet. Upload records to generate a summary."}</p>
              {summary_source && <span className="summary-source">{summary_source}</span>}
            </div>

            <div className="stats-row">
              <div className="stat-card accent-card">
                <div className="sc-label">Gestational Age</div>
                <div className="sc-value">{ga_label.replace("GA ", "")}</div>
                <div className="sc-sub">weeks + days</div>
              </div>
              {edd && (
                <div className="stat-card">
                  <div className="sc-label">Expected Delivery</div>
                  <div className="sc-value">{fmtDate(edd).split(" ").slice(0,2).join(" ")}</div>
                  <div className="sc-sub">{fmtDate(edd).split(" ")[2]}</div>
                </div>
              )}
              <div className="stat-card">
                <div className="sc-label">Documents</div>
                <div className="sc-value">{document_count}</div>
                <div className="sc-sub">uploaded records</div>
              </div>
              <div className="stat-card">
                <div className="sc-label">Attention Items</div>
                <div className="sc-value" style={{ color: attentionCount > 0 ? "var(--warn)" : "var(--ok)" }}>
                  {attentionCount}
                </div>
                <div className="sc-sub">gaps / flags</div>
              </div>
            </div>

            <div className="two-col">
              <div className="card">
                <div className="card-header">
                  <div className="section-title">
                    Attention Required
                    {attentionCount > 0 && <span className="warn-badge">{attentionCount}</span>}
                  </div>
                </div>
                <GapPanel gaps={gaps} qualityFlags={quality_flags} />
              </div>
              <div className="card">
                <div className="card-header">
                  <div className="section-title">
                    Previous vs Latest Values
                  </div>
                </div>
                <div style={{ overflowX: "auto" }}>
                  <TrendTable trends={trends} fmtDate={fmtDate} />
                </div>
              </div>
            </div>

            {quality_flags.length > 0 && (
              <div className="full-section">
                <div className="card">
                  <div className="card-header">
                    <div className="section-title">Record Quality Flags
                      {conflictCount > 0 && <span className="warn-badge">{conflictCount} conflict{conflictCount > 1 ? "s" : ""}</span>}
                    </div>
                  </div>
                  <div className="card-body">
                    {quality_flags.map((f, i) => (
                      <div key={i} className="quality-flag">
                        <div className="qf-icon">{f.kind === "conflict" ? "⚠️" : "ℹ️"}</div>
                        <div className="qf-text">{f.message}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </>
        )}

        {/* INVESTIGATIONS ─────────────────────────────────────────────────── */}
        {activeTab === "investigations" && (
          <>
            <div className="full-section">
              <div className="card">
                <div className="card-header">
                  <div className="section-title">Blood Investigation Trends</div>
                </div>
                <div style={{ overflowX: "auto" }}>
                  <table className="trends-table">
                    <thead>
                      <tr>
                        <th>Test</th>
                        <th>Previous</th>
                        <th>Latest</th>
                        <th>Unit</th>
                        <th>Source</th>
                      </tr>
                    </thead>
                    <tbody>
                      {trends
                        .filter((t) => ["hb","tlc","platelets","fbs","ppbs","hba1c","tsh","creatinine","sgpt","sgot","weight","wt"].includes(t.code))
                        .map((t) => (
                          <tr key={t.code}>
                            <td><strong>{t.label}</strong></td>
                            <td>
                              {t.prev ? (
                                <>
                                  <span className="val-mono">{t.prev.value}</span>
                                  {t.prev.ga_weeks != null && (
                                    <small style={{ color: "var(--fg-3)", marginLeft: 4 }}>
                                      @ {gaFmt(t.prev.ga_weeks)}
                                    </small>
                                  )}
                                </>
                              ) : <span style={{ color: "var(--fg-3)" }}>—</span>}
                            </td>
                            <td>
                              {t.latest ? (
                                <>
                                  <span className="val-mono">{t.latest.value}</span>
                                  {t.latest.ga_weeks != null && (
                                    <small style={{ color: "var(--fg-3)", marginLeft: 4 }}>
                                      @ {gaFmt(t.latest.ga_weeks)}
                                    </small>
                                  )}
                                </>
                              ) : <span style={{ color: "var(--fg-3)" }}>—</span>}
                            </td>
                            <td><span style={{ color: "var(--fg-3)", fontSize: 11 }}>{t.unit ?? "—"}</span></td>
                            <td>
                              {t.latest?.doc_id && (
                                <span className="source-link"
                                  onClick={() => import("../api").then(({ openDoc }) => openDoc(t.latest!.doc_id))}>
                                  View ↗
                                </span>
                              )}
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <div className="full-section">
              <div className="card">
                <div className="card-header">
                  <div className="section-title">Serology & Blood Group</div>
                </div>
                <div className="card-body">
                  {serologyRows.length === 0 ? (
                    <div className="gap-item"><div className="gap-dot dot-info" />
                      <div><div className="gap-label">No serology results found in uploaded records</div></div>
                    </div>
                  ) : serologyRows.map(({ code, obs }) => {
                    const isNR = (obs.value_text ?? "").toLowerCase().includes("non");
                    const isBG = code === "blood_group";
                    return (
                      <div key={code} className="sero-row">
                        <div className="sero-label">{obs.label}</div>
                        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                          <span className={`sero-val ${isBG ? "sero-bg" : isNR ? "sero-nr" : "sero-r"}`}>
                            {obs.value_text ?? "—"}
                          </span>
                          <span className="sero-date">{fmtDate(obs.observed_on)}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </>
        )}

        {/* VITALS ─────────────────────────────────────────────────────────── */}
        {activeTab === "vitals" && (
          <>
            <div className="full-section">
              <div className="card">
                <div className="card-header">
                  <div className="section-title">Blood Pressure Trend</div>
                </div>
                {bpReadings.length === 0 ? (
                  <div className="gap-item" style={{ padding: 16 }}>
                    <div className="gap-dot dot-info" />
                    <div className="gap-label">No BP readings extracted from uploaded records</div>
                  </div>
                ) : (
                  <>
                    <BPChart readings={bpReadings} />
                    <div className="bp-legend">
                      <span><span className="bp-legend-dot" style={{ background: "var(--accent)" }} />Systolic</span>
                      <span><span className="bp-legend-dot" style={{ background: "var(--info)", opacity: 0.7 }} />Diastolic</span>
                    </div>
                  </>
                )}
              </div>
            </div>

            {weightTrend && (
              <div className="full-section">
                <div className="card">
                  <div className="card-header">
                    <div className="section-title">Weight Trend</div>
                  </div>
                  <div style={{ overflowX: "auto" }}>
                    <table className="trends-table">
                      <thead>
                        <tr><th>Date</th><th>GA</th><th>Weight</th><th>Change</th></tr>
                      </thead>
                      <tbody>
                        {weightTrend.history.map((pt, i) => {
                          const prev = weightTrend.history[i - 1];
                          const diff = prev ? pt.value - prev.value : null;
                          return (
                            <tr key={i}>
                              <td>{fmtDate(pt.date)}</td>
                              <td><span className="val-mono" style={{ fontSize: 11 }}>{gaFmt(pt.gestation_weeks)}</span></td>
                              <td><span className="val-mono">{pt.value}</span> <span className="val-unit">kg</span></td>
                              <td>
                                {diff != null ? (
                                  <span className="change-down">+{diff.toFixed(1)}</span>
                                ) : <span className="change-flat">—</span>}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
          </>
        )}

        {/* SCANS ──────────────────────────────────────────────────────────── */}
        {activeTab === "scans" && (
          <>
            {scanEvents.length === 0 ? (
              <div className="card">
                <div style={{ padding: "40px 20px", textAlign: "center", color: "var(--fg-3)" }}>
                  No scan reports found in uploaded records. Upload USG or scan reports to extract findings.
                </div>
              </div>
            ) : scanEvents.map((ev) => {
              const scanObs = ev.observations.filter((o) =>
                ["nt_mm","crl","fhr","efw","afi","presentation","placenta","scan_ga"].includes(o.code)
              );
              return (
                <div key={ev.doc_id} className="card scan-card full-section">
                  <div className="card-header">
                    <div>
                      <div className="section-title">{docTypeLabel(ev.doc_type)}</div>
                      <div style={{ fontSize: 11, color: "var(--fg-3)", marginTop: 2 }}>
                        Date: {fmtDate(ev.date)} · GA at scan: {gaFmt(ev.gestation_weeks)}
                      </div>
                    </div>
                    <span className="source-link"
                      onClick={() => import("../api").then(({ openDoc }) => openDoc(ev.doc_id))}>
                      View source ↗
                    </span>
                  </div>
                  {scanObs.length > 0 && (
                    <div style={{ overflowX: "auto" }}>
                      <table className="trends-table" style={{ minWidth: 280 }}>
                        <thead><tr><th>Finding</th><th>Value</th></tr></thead>
                        <tbody>
                          {scanObs.map((o, i) => (
                            <tr key={i}>
                              <td style={{ color: "var(--fg-3)" }}>{o.label}</td>
                              <td className="val-mono">
                                {o.value_num ?? o.value_text ?? "—"}
                                {o.unit && <span className="val-unit">{o.unit}</span>}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                  <div style={{ padding: "10px 16px", fontSize: 12.5, color: "var(--fg-3)", borderTop: "1px solid var(--border)", background: "var(--bg)" }}>
                    Source: {ev.observations[0]?.snippet || "—"}
                  </div>
                </div>
              );
            })}

            {/* Missing scan gaps */}
            {gaps.filter((g) => g.status === "not_found" && g.id.includes("scan")).map((g) => (
              <div key={g.id} className="card scan-card full-section scan-missing">
                <div className="card-header" style={{ background: "var(--warn-bg)" }}>
                  <div>
                    <div className="section-title">{g.label}</div>
                    <div style={{ fontSize: 11, color: "var(--fg-3)", marginTop: 2 }}>
                      {g.window_weeks ? `Expected window: ${g.window_weeks[0]}–${g.window_weeks[1]} weeks` : ""}
                    </div>
                  </div>
                  <span className="gap-status status-not_found">Not found</span>
                </div>
                <div style={{ padding: "12px 16px", fontSize: 12.5, color: "var(--fg-3)" }}>
                  Not found in uploaded records.
                </div>
              </div>
            ))}
          </>
        )}

        {/* IMMUNO ─────────────────────────────────────────────────────────── */}
        {activeTab === "immuno" && (
          <>
            <div className="full-section">
              <div className="card">
                <div className="card-header">
                  <div className="section-title">Immunisation Record</div>
                </div>
                <div className="card-body">
                  {vaccRows.length === 0 ? (
                    <div className="gap-item">
                      <div className="gap-dot dot-info" />
                      <div><div className="gap-label">No vaccine records found in uploaded records</div></div>
                    </div>
                  ) : vaccRows.map(({ code, obs }) => (
                    <div key={code} className="gap-item">
                      <div className="gap-dot dot-ok" />
                      <div>
                        <div className="gap-label">{obs.label}</div>
                        <div className="gap-sub">
                          Given {fmtDate(obs.observed_on)}
                          {obs.gestation_weeks != null && ` · ${gaFmt(obs.gestation_weeks)}`}
                        </div>
                      </div>
                      <div className="gap-right"><span className="gap-status status-found">Given</span></div>
                    </div>
                  ))}
                  {gaps.filter((g) => ["tt1","tt2"].includes(g.id) && g.status !== "found").map((g) => (
                    <div key={g.id} className="gap-item">
                      <div className="gap-dot dot-info" />
                      <div>
                        <div className="gap-label">{g.label}</div>
                        <div className="gap-sub">Not found in uploaded records
                          {g.window_weeks ? ` · Window: ${g.window_weeks[0]}–${g.window_weeks[1]} wks` : ""}
                        </div>
                      </div>
                      <div className="gap-right">
                        <span className={`gap-status status-${g.status}`}>{g.status.replace("_", " ")}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="full-section">
              <div className="card">
                <div className="card-header">
                  <div className="section-title">Current Medications</div>
                </div>
                <div className="card-body">
                  {medObs.length === 0 ? (
                    <div className="gap-item">
                      <div className="gap-dot" style={{ background: "var(--fg-3)" }} />
                      <div><div className="gap-label">No prescription found in uploaded records</div></div>
                    </div>
                  ) : medObs.map((o, i) => (
                    <div key={i} className="gap-item" style={{ alignItems: "center" }}>
                      <div className="gap-dot" style={{ background: "var(--accent)" }} />
                      <div className="gap-label" style={{ fontWeight: 400 }}>
                        {o.value_text ?? o.snippet}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </>
        )}

        {/* JOURNEY ────────────────────────────────────────────────────────── */}
        {activeTab === "journey" && (
          <div className="full-section">
            <div className="card">
              <div className="card-header">
                <div className="section-title">Chronological Visit & Record Timeline</div>
              </div>
              <Timeline events={events} fmtDate={fmtDate} />
            </div>
          </div>
        )}

        {/* DOCUMENTS ──────────────────────────────────────────────────────── */}
        {activeTab === "documents" && (
          <>
            <div
              className="upload-zone"
              onDragOver={(e) => { e.preventDefault(); e.currentTarget.classList.add("dragover"); }}
              onDragLeave={(e) => e.currentTarget.classList.remove("dragover")}
              onDrop={(e) => { e.preventDefault(); e.currentTarget.classList.remove("dragover"); onUpload(); }}
              onClick={onUpload}
            >
              <div className="upload-icon">⬆</div>
              <div className="upload-title">Drop records here or click to upload</div>
              <div className="upload-sub">Scanned reports, lab PDFs, photos of records</div>
              <div className="file-types">
                {["PDF","PNG","JPG","TXT"].map((t) => (
                  <span key={t} className="file-type-chip">{t}</span>
                ))}
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <div className="section-title">
                  Uploaded Records
                  <span className="count-badge">{document_count}</span>
                </div>
              </div>
              <div>
                {events.length === 0 ? (
                  <div style={{ padding: "24px 16px", textAlign: "center", color: "var(--fg-3)", fontSize: 13 }}>
                    No documents uploaded yet. Use the upload zone above.
                  </div>
                ) : events.map((ev) => {
                  const { icon, cls } = docTypeIcon(ev.doc_type);
                  return (
                    <div key={ev.doc_id} className="doc-row"
                      onClick={() => import("../api").then(({ openDoc }) => openDoc(ev.doc_id))}>
                      <div className={`doc-icon ${cls}`}>{icon}</div>
                      <div style={{ minWidth: 0 }}>
                        <div className="doc-name">{ev.original_filename}</div>
                        <div className="doc-meta">
                          <span>{docTypeLabel(ev.doc_type)}</span>
                          <span>·</span>
                          <span>{fmtDate(ev.date)}</span>
                        </div>
                      </div>
                      <div className="doc-right">
                        <div className="doc-ga">{gaFmt(ev.gestation_weeks)}</div>
                        <div style={{ fontSize: 11, color: "var(--accent)", marginTop: 2 }}>View ↗</div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </>
        )}

      </div>
    </>
  );
}

// ── BP mini-chart ─────────────────────────────────────────────────────────────
function BPChart({ readings }: { readings: { date: string; ga: string; sys: number; dia: number }[] }) {
  const maxSys = Math.max(...readings.map((r) => r.sys));
  const H = 50;
  return (
    <div className="bp-bars">
      {readings.map((r, i) => {
        const sh = Math.round((r.sys / maxSys) * H);
        const dh = Math.round((r.dia / maxSys) * H);
        return (
          <div key={i} className="bp-bar-group">
            <div className="bp-bar-wrap">
              <div className="bp-bar bp-sys" style={{ height: sh }} title={`Systolic ${r.sys}`} />
              <div className="bp-bar bp-dia" style={{ height: dh }} title={`Diastolic ${r.dia}`} />
            </div>
            <div className="bp-label">{r.sys}/{r.dia}</div>
            <div className="bp-date">{r.date}</div>
          </div>
        );
      })}
    </div>
  );
}
