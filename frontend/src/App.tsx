import React, { useState, useEffect, useCallback } from "react";
import { listPatients, getBriefing, seedDemo, createPatient } from "./api";
import type { PatientCard, PatientT, Briefing } from "./types";
import BriefingView from "./components/BriefingView";
import NewPatientForm from "./components/NewPatientForm";
import UploadModal from "./components/UploadModal";

// ── Util ─────────────────────────────────────────────────────────────────────
function fmtDate(iso: string | null): string {
  if (!iso) return "—";
  const [y, m, d] = iso.split("-");
  const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  return `${d} ${months[parseInt(m) - 1]} ${y}`;
}

function riskLabel(briefing: Briefing | null): { label: string; cls: string } {
  if (!briefing) return { label: "Routine", cls: "risk-normal" };
  const hasCritical = briefing.gaps.some((g) => g.status === "not_found") ||
    briefing.quality_flags.some((f) => f.kind === "conflict");
  return hasCritical
    ? { label: "⚑ Attention", cls: "risk-high" }
    : { label: "Routine", cls: "risk-normal" };
}

// ── App ───────────────────────────────────────────────────────────────────────
export default function App() {
  const [patients, setPatients] = useState<PatientCard[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [briefing, setBriefing] = useState<Briefing | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [seeding, setSeeding] = useState(false);
  const [search, setSearch] = useState("");
  const [showNewPatient, setShowNewPatient] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [briefingCache, setBriefingCache] = useState<Record<number, Briefing>>({});

  const loadPatients = useCallback(async () => {
    try {
      const ps = await listPatients();
      setPatients(ps);
    } catch {
      // Backend not running — that's OK in demo mode
    }
  }, []);

  useEffect(() => { loadPatients(); }, [loadPatients]);

  const selectPatient = useCallback(async (id: number) => {
    setSelectedId(id);
    if (briefingCache[id]) {
      setBriefing(briefingCache[id]);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const b = await getBriefing(id);
      setBriefing(b);
      setBriefingCache((c) => ({ ...c, [id]: b }));
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }, [briefingCache]);

  const handleSeedDemo = async () => {
    setSeeding(true);
    setError(null);
    try {
      const result = await seedDemo();
      await loadPatients();
      selectPatient(result.patient_id);
    } catch (e) {
      setError(`Demo seed failed: ${e}`);
    } finally {
      setSeeding(false);
    }
  };

  const handleCreatePatient = async (data: Partial<PatientT>) => {
    const p = await createPatient(data) as unknown as PatientCard;
    setPatients((prev) => [...prev, p]);
    setShowNewPatient(false);
    selectPatient(p.id);
  };

  const refreshBriefing = async () => {
    if (!selectedId) return;
    setBriefingCache((c) => { const n = { ...c }; delete n[selectedId]; return n; });
    selectPatient(selectedId);
  };

  const filteredPatients = patients.filter((p) =>
    p.name.toLowerCase().includes(search.toLowerCase())
  );

  const gaLabel = (p: PatientCard, b: Briefing | null) =>
    b?.ga_label ?? (p.ga ? `GA ${p.ga}` : "GA —");

  return (
    <div className="app">
      {/* ── Sidebar ─────────────────────────────────────────────────────── */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="wordmark">Consult<span>Lens</span></div>
          <div className="tagline">Pre-consultation Briefing · Antenatal</div>
        </div>
        <div className="sidebar-search">
          <input
            type="text"
            placeholder="Search patients…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="sidebar-section-label">Today's Clinic</div>
        <div className="patient-list">
          {filteredPatients.length === 0 && !seeding && (
            <div style={{ padding: "16px", fontSize: "12px", color: "var(--fg-inv-2)", textAlign: "center" }}>
              No patients yet. Load demo or add a patient.
            </div>
          )}
          {filteredPatients.map((p) => {
            const b = briefingCache[p.id] ?? null;
            const risk = riskLabel(b);
            return (
              <div
                key={p.id}
                className={`patient-item${selectedId === p.id ? " active" : ""}`}
                onClick={() => selectPatient(p.id)}
              >
                <div className="patient-name">{p.name}</div>
                <div className="patient-meta">
                  <span className="ga-badge">{gaLabel(p, b)}</span>
                  <span className={`risk-badge ${risk.cls}`}>{risk.label}</span>
                </div>
              </div>
            );
          })}
        </div>
        <div className="sidebar-footer">
          <button className="demo-btn" onClick={handleSeedDemo} disabled={seeding}>
            {seeding ? "⏳ Loading demo…" : "⚡ Load demo patient"}
          </button>
          <button className="add-patient-btn" onClick={() => setShowNewPatient(true)}>
            + New Patient
          </button>
        </div>
      </aside>

      {/* ── Main ────────────────────────────────────────────────────────── */}
      <main className="main">
        {loading && (
          <div className="loading-overlay">
            <div className="spinner" style={{ width: 24, height: 24 }} />
            <span>Loading briefing…</span>
          </div>
        )}
        {!loading && !briefing && (
          <div className="empty-state" style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
            {error && <div className="error-banner" style={{ maxWidth: 420, marginBottom: 16 }}>{error}</div>}
            <div className="es-icon">🩺</div>
            <div className="es-title">No patient selected</div>
            <div className="es-sub">
              Select a patient from the sidebar<br />
              or click <strong>Load demo patient</strong> to see a live briefing.
            </div>
          </div>
        )}
        {!loading && briefing && (
          <BriefingView
            briefing={briefing}
            onUpload={() => setShowUpload(true)}
            onRefresh={refreshBriefing}
            fmtDate={fmtDate}
          />
        )}
      </main>

      {/* ── Modals ──────────────────────────────────────────────────────── */}
      {showNewPatient && (
        <NewPatientForm
          onSave={handleCreatePatient}
          onClose={() => setShowNewPatient(false)}
        />
      )}
      {showUpload && briefing && (
        <UploadModal
          patientId={briefing.patient.id}
          onClose={() => setShowUpload(false)}
          onDone={refreshBriefing}
        />
      )}
    </div>
  );
}
