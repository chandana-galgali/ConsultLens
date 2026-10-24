import React, { useState, useRef } from "react";
import { uploadDoc } from "../api";

interface Props {
  patientId: number;
  onClose: () => void;
  onDone: () => void;
}

interface FileState {
  file: File;
  progress: number;
  status: "pending" | "uploading" | "done" | "error";
  error?: string;
}

const ACCEPT = ".pdf,.png,.jpg,.jpeg,.txt,.tif,.tiff";
const MAX_MB = 20;

export default function UploadModal({ patientId, onClose, onDone }: Props) {
  const [files, setFiles] = useState<FileState[]>([]);
  const [dragover, setDragover] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  function addFiles(incoming: FileList | null) {
    if (!incoming) return;
    const newStates: FileState[] = [];
    for (let i = 0; i < incoming.length; i++) {
      const f = incoming[i];
      if (f.size > MAX_MB * 1024 * 1024) {
        newStates.push({ file: f, progress: 0, status: "error", error: `File too large (max ${MAX_MB} MB)` });
      } else {
        newStates.push({ file: f, progress: 0, status: "pending" });
      }
    }
    setFiles((prev) => [...prev, ...newStates]);
  }

  async function uploadAll() {
    const pending = files.filter((f) => f.status === "pending");
    if (pending.length === 0) return;
    await Promise.all(
      pending.map(async (fs, _) => {
        const idx = files.findIndex((x) => x.file === fs.file);
        setFiles((prev) =>
          prev.map((x, i) => (x.file === fs.file ? { ...x, status: "uploading" } : x))
        );
        try {
          await uploadDoc(patientId, fs.file, (pct) => {
            setFiles((prev) =>
              prev.map((x) => (x.file === fs.file ? { ...x, progress: pct } : x))
            );
          });
          setFiles((prev) =>
            prev.map((x) => (x.file === fs.file ? { ...x, status: "done", progress: 100 } : x))
          );
        } catch (e) {
          setFiles((prev) =>
            prev.map((x) => (x.file === fs.file ? { ...x, status: "error", error: String(e) } : x))
          );
        }
      })
    );
    const allDone = files.every((f) => f.status === "done" || f.status === "error");
    if (allDone) {
      setTimeout(() => { onDone(); onClose(); }, 800);
    }
  }

  const allDone = files.length > 0 && files.every((f) => f.status === "done");
  const hasPending = files.some((f) => f.status === "pending");
  const uploading = files.some((f) => f.status === "uploading");

  function extIcon(name: string): string {
    if (name.endsWith(".pdf")) return "📄";
    if (/\.(png|jpg|jpeg|tif|tiff)$/.test(name)) return "🖼";
    return "📝";
  }

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-header">
          <div className="modal-title">Upload Records</div>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <div
          className={`upload-zone${dragover ? " dragover" : ""}`}
          style={{ margin: "16px", marginBottom: 0 }}
          onDragOver={(e) => { e.preventDefault(); setDragover(true); }}
          onDragLeave={() => setDragover(false)}
          onDrop={(e) => { e.preventDefault(); setDragover(false); addFiles(e.dataTransfer.files); }}
          onClick={() => inputRef.current?.click()}
        >
          <input
            ref={inputRef}
            type="file"
            accept={ACCEPT}
            multiple
            style={{ display: "none" }}
            onChange={(e) => addFiles(e.target.files)}
          />
          <div className="upload-icon">⬆</div>
          <div className="upload-title">Drop files here or click to browse</div>
          <div className="upload-sub">Scanned lab reports, USG films, ANC cards, prescriptions</div>
          <div className="file-types">
            {["PDF","PNG","JPG","TIF","TXT"].map((t) => (
              <span key={t} className="file-type-chip">{t}</span>
            ))}
          </div>
        </div>

        {files.length > 0 && (
          <div style={{ padding: "12px 16px" }}>
            {files.map((fs, i) => (
              <div key={i} className="upload-file-row">
                <div className="upload-file-icon">{extIcon(fs.file.name)}</div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div className="upload-file-name">{fs.file.name}</div>
                  <div className="upload-file-size">{(fs.file.size / 1024).toFixed(0)} KB</div>
                  {fs.status === "uploading" && (
                    <div className="upload-progress-bar">
                      <div className="upload-progress-fill" style={{ width: `${fs.progress}%` }} />
                    </div>
                  )}
                  {fs.status === "error" && (
                    <div style={{ fontSize: 11, color: "var(--danger)", marginTop: 2 }}>{fs.error}</div>
                  )}
                </div>
                <div className="upload-file-status">
                  {fs.status === "done" && <span style={{ color: "var(--ok)" }}>✓</span>}
                  {fs.status === "error" && <span style={{ color: "var(--danger)" }}>✗</span>}
                  {fs.status === "uploading" && <span style={{ color: "var(--accent)" }}>{fs.progress}%</span>}
                  {fs.status === "pending" && (
                    <span
                      style={{ color: "var(--fg-3)", cursor: "pointer", fontSize: 16 }}
                      onClick={(e) => { e.stopPropagation(); setFiles((prev) => prev.filter((_, j) => j !== i)); }}
                    >×</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="modal-footer">
          <button className="btn btn-ghost" onClick={onClose} disabled={uploading}>
            Cancel
          </button>
          <button
            className="btn btn-primary"
            onClick={uploadAll}
            disabled={!hasPending || uploading}
          >
            {uploading ? (
              <><span className="spinner" style={{ width: 14, height: 14, marginRight: 6 }} />Uploading…</>
            ) : allDone ? (
              "✓ All uploaded"
            ) : (
              `Upload ${files.filter((f) => f.status === "pending").length} file${files.filter((f) => f.status === "pending").length > 1 ? "s" : ""}`
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
