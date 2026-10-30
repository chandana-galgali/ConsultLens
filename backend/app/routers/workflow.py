"""Human-reviewed voice note drafts and opt-in reminder queue.

Provider remains mock unless a real integration has been independently configured.
"""
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .. import models
from ..db import get_db
from ..config import settings
import httpx
import logging

logger = logging.getLogger(__name__)
from ..security import current_user, require_roles

router = APIRouter(prefix="/workflow", tags=["workflow"])
LANGS = {"en", "hi", "mr"}

class NoteIn(BaseModel):
    transcript: str = Field(min_length=1, max_length=20000)
    reviewed_text: str = Field(min_length=1, max_length=20000)
    language: str = "en"

class ReminderIn(BaseModel):
    scheduled_for: datetime
    language: str = "en"

MESSAGES = {
    "en": "Your clinic appointment is scheduled for {date}. Please contact the clinic if you need to change it.",
    "hi": "आपकी क्लिनिक अपॉइंटमेंट {date} को निर्धारित है। बदलाव के लिए क्लिनिक से संपर्क करें।",
    "mr": "आपली क्लिनिक भेट {date} रोजी निश्चित आहे. बदलासाठी क्लिनिकशी संपर्क साधा.",
}

def patient_or_404(db: Session, pid: int) -> models.Patient:
    patient = db.get(models.Patient, pid)
    if not patient:
        raise HTTPException(404, "Patient not found")
    return patient

@router.post("/patients/{pid}/notes", status_code=201)
def save_note(pid: int, body: NoteIn, db: Session = Depends(get_db),
              user: models.StaffUser = Depends(require_roles("doctor", "nurse"))):
    patient_or_404(db, pid)
    if body.language not in LANGS:
        raise HTTPException(422, "Unsupported language")
    note = models.ClinicalNote(patient_id=pid, author_id=user.id, language=body.language,
                               transcript=body.transcript, reviewed_text=body.reviewed_text)
    db.add(note); db.flush()
    db.add(models.AuditEntry(actor_id=user.id, action="note_approved", patient_id=pid))
    db.commit(); db.refresh(note)
    return {"id": note.id, "created_at": note.created_at, "reviewed_text": note.reviewed_text}

@router.get("/patients/{pid}/notes")
def list_notes(pid: int, db: Session = Depends(get_db), user: models.StaffUser = Depends(current_user)):
    patient_or_404(db, pid)
    return [{"id": n.id, "language": n.language, "reviewed_text": n.reviewed_text, "created_at": n.created_at}
            for n in db.query(models.ClinicalNote).filter_by(patient_id=pid).order_by(models.ClinicalNote.id.desc()).all()]

@router.post("/patients/{pid}/reminders", status_code=201)
def queue_reminder(pid: int, body: ReminderIn, db: Session = Depends(get_db),
                   user: models.StaffUser = Depends(require_roles("doctor", "nurse"))):
    patient = patient_or_404(db, pid)
    if not patient.reminder_opt_in or not patient.phone:
        raise HTTPException(409, "Patient requires a validated phone and recorded messaging consent")
    if body.language not in LANGS:
        raise HTTPException(422, "Unsupported language")
    when = body.scheduled_for
    if when.tzinfo is None:
        raise HTTPException(422, "Time zone offset required")
    if when <= datetime.now(timezone.utc):
        raise HTTPException(422, "Scheduled time must be in future")
    body_text = MESSAGES[body.language].format(date=when.strftime("%d %b %Y %H:%M %Z"))
    reminder = models.Reminder(patient_id=pid, author_id=user.id, scheduled_for=when.replace(tzinfo=None),
                               language=body.language, body=body_text, status="queued_mock")
    db.add(reminder); db.flush()
    db.add(models.AuditEntry(actor_id=user.id, action="reminder_queued_mock", patient_id=pid))
    db.commit(); db.refresh(reminder)
    return {"id": reminder.id, "status": reminder.status, "message": reminder.body,
            "notice": "Mock provider: no WhatsApp/SMS was sent"}

@router.get("/patients/{pid}/reminders")
def reminders(pid: int, db: Session = Depends(get_db), user: models.StaffUser = Depends(current_user)):
    patient_or_404(db, pid)
    return [{"id": r.id, "scheduled_for": r.scheduled_for, "language": r.language, "status": r.status, "body": r.body}
            for r in db.query(models.Reminder).filter_by(patient_id=pid).order_by(models.Reminder.id.desc()).all()]


@router.post("/transcribe")
async def transcribe_demo_audio(
    file: UploadFile = File(...),
    language: str = Form("en"),
    synthetic_consent: bool = Form(False),
    _user: models.StaffUser = Depends(require_roles("doctor", "nurse")),
):
    """Explicit synthetic-only demo transcription; never persists raw audio or auto-approves notes."""
    if not synthetic_consent:
        raise HTTPException(422, "Confirm that this recording contains synthetic, consented demonstration content")
    if language not in LANGS:
        raise HTTPException(422, "Unsupported transcription language")
    if not settings.openai_api_key:
        raise HTTPException(503, "Audio AI transcription is not configured. Use browser dictation or typed notes")
    suffix = (file.filename or "").lower().rsplit(".", 1)[-1]
    if suffix not in {"wav", "mp3", "mp4", "m4a", "webm", "ogg"}:
        raise HTTPException(422, "Upload a WAV, MP3, MP4, M4A, WebM or OGG recording")
    max_bytes = 12 * 1024 * 1024
    audio = await file.read(max_bytes + 1)
    if len(audio) > max_bytes:
        raise HTTPException(413, "Audio is too large (12 MB limit)")
    if not audio:
        raise HTTPException(422, "Audio recording is empty")
    try:
        async with httpx.AsyncClient(timeout=70) as client:
            response = await client.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                data={"model": settings.audio_transcription_model, "language": language},
                files={"file": (file.filename or f"demo.{suffix}", audio, file.content_type or "application/octet-stream")},
            )
            response.raise_for_status()
            text = response.json().get("text", "")
            if not isinstance(text, str) or not text.strip():
                raise ValueError("Empty transcription")
            return {"transcript": text, "language": language, "status": "draft_requires_human_review"}
    except (httpx.HTTPError, ValueError, KeyError):
        logger.exception("demo_audio_transcription_failed")
        raise HTTPException(502, "Transcription provider unavailable or returned an invalid response") from None
