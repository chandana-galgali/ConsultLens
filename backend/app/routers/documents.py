import mimetypes
import uuid
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import models
from ..catalog import DOC_TYPE_LABELS
from ..config import settings
from ..db import get_db
from ..security import require_roles
from ..services.pipeline import process_document, reextract_document
from ..services.timeline_builder import fmt_ga

router = APIRouter(tags=["documents"])
ALLOWED = {".pdf", ".png", ".jpg", ".jpeg", ".txt"}
SOURCES = {"upload", "whatsapp", "emr"}


def _summary(db, doc: models.Document) -> dict:
    n = db.query(models.Observation).filter_by(document_id=doc.id).all()
    return {
        "id": doc.id, "filename": doc.filename, "doc_type": doc.doc_type, "doc_date": doc.doc_date,
        "ga": fmt_ga(doc.patient.lmp, doc.doc_date), "source": doc.source, "ocr_engine": doc.ocr_engine,
        "ocr_confidence": doc.ocr_confidence if isinstance(doc.ocr_confidence, (int, float)) else None,
        "values": len([o for o in n if o.code != "plan"]),
    }


@router.post("/patients/{pid}/documents")
def upload(pid: int, file: UploadFile = File(...), source: str = Form("upload"),
           doc_date: date | None = Form(None), db: Session = Depends(get_db),
           _user=Depends(require_roles("admin", "doctor", "nurse", "lab"))):
    patient = db.get(models.Patient, pid)
    if not patient:
        raise HTTPException(404, "Patient not found")
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED:
        raise HTTPException(400, f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(ALLOWED))}")
    if source not in SOURCES:
        source = "upload"

    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    stored = Path(settings.upload_dir) / f"{uuid.uuid4().hex}{ext}"
    try:
        with stored.open("wb") as f:
            total = 0
            while part := file.file.read(1024 * 1024):
                total += len(part)
                if total > settings.max_upload_mb * 1024 * 1024:
                    raise HTTPException(413, "Upload exceeds configured limit")
                f.write(part)
    except Exception:
        stored.unlink(missing_ok=True)
        raise

    doc = models.Document(patient_id=pid, filename=file.filename, stored_path=str(stored), source=source)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    try:
        doc = process_document(db, doc, user_date=doc_date)
    except Exception:  # parsing errors are not disclosed to callers
        db.delete(doc)
        db.commit()
        stored.unlink(missing_ok=True)
        raise HTTPException(422, "Could not process document; check that it is a supported, readable file")
    return _summary(db, doc)


@router.get("/documents/{did}/file")
def get_file(did: int, db: Session = Depends(get_db)):
    d = db.get(models.Document, did)
    if not d:
        raise HTTPException(404, "Document not found")
    media = mimetypes.guess_type(d.filename or "")[0] or "application/octet-stream"
    return FileResponse(d.stored_path, media_type=media, filename=d.filename, content_disposition_type="inline")


@router.get("/documents/{did}/text")
def get_text(did: int, db: Session = Depends(get_db)):
    d = db.get(models.Document, did)
    if not d:
        raise HTTPException(404, "Document not found")
    return {"filename": d.filename, "ocr_engine": d.ocr_engine, "ocr_confidence": d.ocr_confidence, "text": d.ocr_text}


class DocumentPatch(BaseModel):
    doc_type: str | None = None
    doc_date: date | None = None


@router.patch("/documents/{did}")
def patch_document(did: int, body: DocumentPatch, db: Session = Depends(get_db),
                   _user=Depends(require_roles("admin", "doctor", "nurse", "lab"))):
    """Clinician fixes the document type or date. Values are re-extracted from the stored text (no new OCR)."""
    d = db.get(models.Document, did)
    if not d:
        raise HTTPException(404, "Document not found")
    changes = body.model_dump(exclude_unset=True)
    if "doc_type" in changes:
        if changes["doc_type"] not in DOC_TYPE_LABELS:
            raise HTTPException(400, f"Unknown document type. Use one of: {', '.join(DOC_TYPE_LABELS)}")
        d.doc_type = changes["doc_type"]
    if "doc_date" in changes:
        d.doc_date = changes["doc_date"]
    db.commit()
    return _summary(db, reextract_document(db, d))


@router.delete("/documents/{did}")
def delete_document(did: int, db: Session = Depends(get_db),
                    _user=Depends(require_roles("admin", "doctor"))):
    d = db.get(models.Document, did)
    if not d:
        raise HTTPException(404, "Document not found")
    db.query(models.Observation).filter_by(document_id=did).delete()
    path = d.stored_path
    db.delete(d)
    db.commit()
    Path(path).unlink(missing_ok=True)
    return {"deleted": did}
