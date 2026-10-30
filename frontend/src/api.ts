// ── API client ────────────────────────────────────────────────────────────────
// Base URL: VITE_API_URL env var, default localhost:8000
// In Care plugin, call configureApi() with the Care token before any request.

// import type { PatientT, PatientCard, Briefing, EventT, Trend, GapItem, QualityFlag, Obs } from "./types";

// let BASE = (import.meta as Record<string, unknown> & { env: Record<string, string> }).env.VITE_API_URL ?? "http://localhost:8000";
// let AUTH_HEADER: Record<string, string> = {};

import type { PatientT, PatientCard, Briefing, EventT, Trend, GapItem, QualityFlag, Obs } from "./types";

const API_BASE_URL = ""; 
let BASE = import.meta.env.VITE_API_URL ?? API_BASE_URL;
let AUTH_HEADER: Record<string, string> = {};

export function configureApi(baseUrl: string, token?: string) {
  BASE = baseUrl.replace(/\/$/, "");
  AUTH_HEADER = token ? { Authorization: `Bearer ${token}` } : {};
}

async function get<T>(path: string): Promise<T> {
  const r = await fetch(`${BASE}${path}`, { headers: AUTH_HEADER });
  if (!r.ok) throw new Error(`GET ${path} → ${r.status}`);
  return r.json();
}

async function post<T>(path: string, body?: unknown): Promise<T> {
  const r = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...AUTH_HEADER },
    body: body != null ? JSON.stringify(body) : undefined,
  });
  if (!r.ok) throw new Error(`POST ${path} → ${r.status}`);
  return r.json();
}

async function patch<T>(path: string, body: unknown): Promise<T> {
  const r = await fetch(`${BASE}${path}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", ...AUTH_HEADER },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`PATCH ${path} → ${r.status}`);
  return r.json();
}

// ── Patients ──────────────────────────────────────────────────────────────────
export const listPatients = () => get<PatientCard[]>("/patients");

export const createPatient = (data: Partial<PatientT>) =>
  post<PatientT>("/patients", {
    name: data.name,
    age: data.age,
    lmp: data.lmp,
    phone: data.phone,
    preferred_language: data.preferred_language ?? "en",
    reminder_opt_in: data.reminder_opt_in ?? false,
  });

export const updatePatient = (id: number, data: Partial<PatientT>) =>
  patch<PatientT>(`/patients/${id}`, data);

// ── GA helpers ────────────────────────────────────────────────────────────────
function gaStringToWeeks(ga: string | null): number | null {
  if (!ga) return null;
  const m = ga.match(/^(\d+)\+(\d)$/);
  if (!m) return null;
  return parseInt(m[1]) + parseInt(m[2]) / 7;
}

function gaLabel(gaStr: string | null): string {
  if (!gaStr) return "GA —";
  return `GA ${gaStr}`;
}

// ── Map raw backend gap item to front-end GapItem ─────────────────────────────
function mapGapItem(raw: Record<string, unknown>): GapItem {
  const rawStatus = String(raw.status ?? "");
  let status: GapItem["status"] = "not_found";
  if (rawStatus === "found") status = "found";
  else if (rawStatus === "due_now" || rawStatus === "window_open") status = "window_open";
  else if (rawStatus === "no_lmp") status = "no_lmp";
  else if (rawStatus === "future" || rawStatus === "upcoming") status = "future";
  else if (rawStatus.includes("not_found")) status = "not_found";

  const win = raw.window as Record<string, number> | string | null;
  return {
    id: String(raw.id ?? raw.code ?? ""),
    label: String(raw.label ?? ""),
    status,
    found_on: raw.found_on ? String(raw.found_on) : null,
    found_ga_weeks: raw.found_ga ? gaStringToWeeks(String(raw.found_ga)) : null,
    window_weeks: win && typeof win === "object" ? [win.start ?? 0, win.end ?? 0] : null,
  };
}

// ── Map raw backend observation (from events) to front-end Obs ────────────────
function mapObs(raw: Record<string, unknown>, docId: number, docDate: string | null, gaW: number | null): Obs {
  const v = raw.value;
  return {
    id: Number(raw.id ?? 0),
    code: String(raw.code ?? ""),
    label: String(raw.label ?? ""),
    value_num: typeof v === "number" ? v : null,
    value_text: typeof v === "string" ? v : null,
    unit: raw.unit ? String(raw.unit) : null,
    observed_on: docDate,
    gestation_weeks: gaW,
    snippet: String(raw.snippet ?? ""),
    document_id: docId,
  };
}

// ── Map raw backend events to front-end EventT ────────────────────────────────
function mapEvents(rawEvents: unknown[]): EventT[] {
  return (rawEvents as Record<string, unknown>[]).map((ev) => {
    const gaStr = ev.ga as string | null;
    const gaW = gaStringToWeeks(gaStr);
    const docId = Number(ev.doc_id ?? 0);
    const docDate = ev.date ? String(ev.date) : null;
    const rawObs = (ev.observations as Record<string, unknown>[]) ?? [];
    return {
      date: docDate,
      ga: gaStr,
      gestation_weeks: gaW,
      doc_id: docId,
      doc_type: ev.doc_type ? String(ev.doc_type) : null,
      original_filename: String(ev.filename ?? ev.original_filename ?? ""),
      observations: rawObs.map((o) => mapObs(o, docId, docDate, gaW)),
    };
  });
}

// ── Map raw backend trends to front-end Trend ─────────────────────────────────
function mapTrends(rawTrends: unknown[]): Trend[] {
  return (rawTrends as Record<string, unknown>[]).map((t) => {
    const latest = t.latest as Record<string, unknown> | null;
    const prev = (t.previous ?? t.prev) as Record<string, unknown> | null;
    const history = ((t.history ?? []) as Record<string, unknown>[]);
    return {
      code: String(t.code ?? ""),
      label: String(t.label ?? ""),
      unit: t.unit ? String(t.unit) : null,
      latest: latest as Trend["latest"],
      prev: prev as Trend["prev"],
      change: t.delta != null ? Number(t.delta) : null,
      history: history as unknown as Trend["history"],
      points: history as unknown as Trend["points"],
    };
  });
}

// ── Map full backend briefing to front-end Briefing ───────────────────────────
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function mapBriefing(raw: Record<string, unknown>): Briefing {
  const pt = (raw.patient as Record<string, unknown>) ?? {};
  const snap = (raw.snapshot as Record<string, unknown>) ?? {};
  const gapData = (raw.gaps as Record<string, unknown>) ?? {};
  const gapItems: GapItem[] = ((gapData.items ?? []) as unknown[]).map((g) =>
    mapGapItem(g as Record<string, unknown>)
  );
  const qualityFlags: QualityFlag[] = ((gapData.quality ?? []) as unknown[]).map((f) => {
    const ff = f as Record<string, unknown>;
    return {
      kind: String(ff.type ?? ff.kind ?? "no_date") as QualityFlag["kind"],
      message: String(ff.message ?? ""),
      doc_id: ff.doc_id != null ? Number(ff.doc_id) : null,
    };
  });

  const rawEvents = (raw.events as unknown[]) ?? [];
  const events = mapEvents(rawEvents);

  const rawTrends = (raw.trends as unknown[]) ?? [];
  const trends = mapTrends(rawTrends);

  // Summary — backend may expose it under narrative or as summary sub-key
  const narrative = (raw.narrative as Record<string, unknown> | string) ?? "";
  const summaryText = typeof narrative === "string"
    ? narrative
    : (narrative?.text as string) ?? (snap.summary as string) ?? "";
  const summarySource = typeof narrative === "object" && narrative
    ? ((narrative?.engine as string) ?? "structured summary")
    : summaryText ? "structured summary" : "No briefing available";

  // The backend snapshot has no `ga` field. Prefer the explicit API value,
  // then calculate from the recorded LMP as a compatibility fallback.
  const rawGa = raw.ga as string | null | undefined;
  const lmpText = typeof pt.lmp === "string" ? pt.lmp : null;
  const lmpDay = lmpText ? Date.parse(`${lmpText}T00:00:00Z`) : NaN;
  const elapsedDays = Number.isFinite(lmpDay)
    ? Math.floor((Date.now() - lmpDay) / 86400000)
    : null;
  const fallbackGa = elapsedDays !== null && elapsedDays >= 0
    ? `${Math.floor(elapsedDays / 7)}+${elapsedDays % 7}` : null;
  const gaStr = typeof rawGa === "string" && /^\d+\+[0-6]$/.test(rawGa)
    ? rawGa : fallbackGa;

  return {
    patient: {
      id: Number(pt.id ?? 0),
      name: String(pt.name ?? ""),
      age: pt.age != null ? Number(pt.age) : null,
      lmp: pt.lmp ? String(pt.lmp) : null,
      edd: pt.edd ? String(pt.edd) : null,
      phone: pt.phone ? String(pt.phone) : null,
      blood_group: pt.blood_group ? String(pt.blood_group) : null,
      mrn: pt.mrn ? String(pt.mrn) : null,
      external_id: pt.external_id ? String(pt.external_id) : null,
      gravida: pt.gravida != null ? Number(pt.gravida) : null,
      para: pt.para != null ? Number(pt.para) : null,
      profile: (pt.profile as Record<string, unknown>) ?? null,
    },
    ga_weeks: gaStringToWeeks(gaStr),
    ga_label: gaStr ? `GA ${gaStr}` : "GA unavailable",
    edd: pt.edd ? String(pt.edd) : null,
    summary: summaryText,
    summary_source: summarySource,
    events,
    trends,
    gaps: gapItems,
    quality_flags: qualityFlags,
    document_count: events.length,
  };
}

// ── Briefing endpoints ─────────────────────────────────────────────────────────
export async function getBriefing(patientId: number): Promise<Briefing> {
  const raw = await get<Record<string, unknown>>(`/patients/${patientId}/briefing?narrative=true`);
  return mapBriefing(raw);
}

export async function getBriefingByExternal(extId: string): Promise<Briefing> {
  const raw = await get<Record<string, unknown>>(`/integrations/external/${extId}/briefing?narrative=true`);
  return mapBriefing(raw);
}

// ── Documents ──────────────────────────────────────────────────────────────────
export interface DocumentT {
  id: number;
  patient_id: number;
  original_filename: string;
  doc_type: string | null;
  doc_date: string | null;
  uploaded_at: string;
}

export async function uploadDoc(
  patientId: number,
  file: File,
  onProgress?: (pct: number) => void
): Promise<DocumentT> {
  const fd = new FormData();
  fd.append("file", file);
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    if (onProgress) {
      xhr.upload.addEventListener("progress", (e) => {
        if (e.lengthComputable) onProgress(Math.round((e.loaded / e.total) * 100));
      });
    }
    xhr.addEventListener("load", () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(JSON.parse(xhr.responseText));
      } else {
        reject(new Error(`Upload failed: ${xhr.status}`));
      }
    });
    xhr.addEventListener("error", () => reject(new Error("Network error")));
    xhr.open("POST", `${BASE}/patients/${patientId}/documents`);
    Object.entries(AUTH_HEADER).forEach(([k, v]) => xhr.setRequestHeader(k, v));
    xhr.send(fd);
  });
}

export async function listDocuments(patientId: number): Promise<DocumentT[]> {
  return get<DocumentT[]>(`/patients/${patientId}/documents`);
}

// ── Source document viewer ─────────────────────────────────────────────────────
export function fileUrl(docId: number): string {
  return `${BASE}/documents/${docId}/file`;
}

export async function openDoc(docId: number): Promise<void> {
  const url = fileUrl(docId);
  try {
    const r = await fetch(url, { headers: AUTH_HEADER });
    if (!r.ok) throw new Error(`${r.status}`);
    const blob = await r.blob();
    window.open(URL.createObjectURL(blob), "_blank");
  } catch {
    window.open(url, "_blank");
  }
}

// ── Demo ───────────────────────────────────────────────────────────────────────
export const seedDemo = () =>
  post<{ message: string; patient_id: number; created_count: number }>("/demo/seed");
