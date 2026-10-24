import React, { useState } from "react";
import type { PatientT } from "../types";

interface Props {
  onSave: (data: Partial<PatientT>) => Promise<void>;
  onClose: () => void;
}

export default function NewPatientForm({ onSave, onClose }: Props) {
  const [form, setForm] = useState({
    name: "",
    age_years: "",
    lmp: "",
    whatsapp_number: "",
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [k]: e.target.value }));

  async function handleSubmit(ev: React.FormEvent) {
    ev.preventDefault();
    if (!form.name.trim()) { setError("Patient name is required"); return; }
    setSaving(true);
    setError(null);
    try {
      await onSave({
        name: form.name.trim(),
        age: form.age_years ? parseInt(form.age_years) : null,
        lmp: form.lmp || null,
        phone: form.whatsapp_number || null,
      });
    } catch (e) {
      setError(String(e));
      setSaving(false);
    }
  }

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal" style={{ maxWidth: 400 }}>
        <div className="modal-header">
          <div className="modal-title">New Patient</div>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit} style={{ padding: "16px" }}>
          {error && (
            <div className="error-banner" style={{ marginBottom: 12 }}>{error}</div>
          )}

          <div className="form-group">
            <label className="form-label">Full Name *</label>
            <input
              className="form-input"
              type="text"
              placeholder="e.g. Priya Sharma"
              value={form.name}
              onChange={set("name")}
              autoFocus
            />
          </div>

          <div className="form-group">
            <label className="form-label">Age (years)</label>
            <input
              className="form-input"
              type="number"
              min="14" max="55"
              placeholder="e.g. 28"
              value={form.age_years}
              onChange={set("age_years")}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Last Menstrual Period (LMP)</label>
            <input
              className="form-input"
              type="date"
              value={form.lmp}
              onChange={set("lmp")}
            />
            <div className="form-hint">Used to calculate gestational age and EDD</div>
          </div>

          <div className="form-group">
            <label className="form-label">WhatsApp Number</label>
            <input
              className="form-input"
              type="tel"
              placeholder="e.g. +91 98765 43210"
              value={form.whatsapp_number}
              onChange={set("whatsapp_number")}
            />
          </div>

          <div className="modal-footer" style={{ padding: 0, paddingTop: 8 }}>
            <button type="button" className="btn btn-ghost" onClick={onClose} disabled={saving}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? "Saving…" : "Add Patient"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
