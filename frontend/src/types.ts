// ── Core API types — aligned with ConsultLens backend shape ──────────────────

export interface PatientT {
  id: number;
  name: string;
  age: number | null;
  lmp: string | null;           // ISO date
  edd: string | null;           // ISO date
  phone: string | null;
  preferred_language?: "en" | "hi" | "mr";
  reminder_opt_in?: boolean;
  blood_group: string | null;
  mrn: string | null;
  external_id: string | null;
  gravida: number | null;
  para: number | null;
  profile: Record<string, unknown> | null;
}

// ── Observation as returned from backend events array ─────────────────────────
export interface ObsRaw {
  id: number;
  code: string;
  label: string;
  value: number | string | null;   // backend sends unified value
  unit: string | null;
  snippet: string;
  verified: boolean;
  edited: boolean;
}

// ── Observation as expected by components (split value_num / value_text) ──────
export interface Obs {
  id: number;
  code: string;
  label: string;
  value_num: number | null;
  value_text: string | null;
  unit: string | null;
  observed_on: string | null;
  gestation_weeks: number | null;
  snippet: string;
  document_id: number;
}

export interface EventT {
  date: string | null;
  ga: string | null;             // formatted "26+4" style
  gestation_weeks: number | null;
  doc_id: number;
  doc_type: string | null;
  original_filename: string;
  observations: Obs[];
}

export interface TrendPoint {
  date: string;
  value: number;
  ga: string | null;
  ga_weeks: number | null;
  gestation_weeks: number | null;
  doc_id: number;
  obs_id: number;
  dia?: number;        // for BP combined trend
  display?: string;
}

export interface Trend {
  code: string;
  label: string;
  unit: string | null;
  latest: TrendPoint | null;
  prev: TrendPoint | null;
  change: number | null;
  history: TrendPoint[];
  // Compatibility shims for TrendTable (points / latest as Obs)
  points: TrendPoint[];
}

export type GapStatus =
  | "found"
  | "not_found"
  | "window_open"
  | "no_lmp"
  | "future";

export interface GapItem {
  id: string;
  label: string;
  status: GapStatus;
  found_on: string | null;
  found_ga_weeks: number | null;
  window_weeks: [number, number] | null;
}

export interface QualityFlag {
  kind: "no_date" | "edd_mismatch" | "conflict" | "future_date" | "before_lmp";
  message: string;
  doc_id: number | null;
}

export interface Briefing {
  patient: PatientT;
  ga_weeks: number | null;
  ga_label: string;
  edd: string | null;
  summary: string;
  summary_source: string;
  events: EventT[];
  trends: Trend[];
  gaps: GapItem[];
  quality_flags: QualityFlag[];
  document_count: number;
}

// ── Patient list card (sidebar) ────────────────────────────────────────────────
export interface PatientCard extends PatientT {
  ga: string | null;
  documents: number;
  not_found: number;
  window_open: number;
  quality_flags: number;
}
