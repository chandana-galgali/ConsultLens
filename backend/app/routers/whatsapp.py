"""OPTIONAL: receive documents a patient sends on WhatsApp (Twilio webhook).

Setup (later, not needed for the MVP demo):
  1. Twilio WhatsApp sandbox -> set "When a message comes in" to  https://<public-url>/webhooks/whatsapp
     (use ngrok or similar to expose localhost).
  2. Put TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in backend/.env.
  3. Make sure Patient.phone matches the sender, e.g. 'whatsapp:+9199...' is stored as '+9199...'.
Not verified against a live Twilio account - covered only by a mocked test."""
import uuid
from pathlib import Path

import httpx
from fastapi import APIRouter, Depends, Form, Response
from sqlalchemy.orm import Session

from .. import models
from ..config import settings
from ..db import get_db
from ..services.pipeline import process_document

router = APIRouter(prefix="/webhooks", tags=["whatsapp"])

EXT_BY_MIME = {"application/pdf": ".pdf", "image/jpeg": ".jpg", "image/png": ".png"}


def download_media(url: str) -> bytes:
    auth = (settings.twilio_account_sid, settings.twilio_auth_token) if settings.twilio_account_sid else None
    r = httpx.get(url, auth=auth, follow_redirects=True, timeout=60)
    r.raise_for_status()
    return r.content


def _twiml(msg: str) -> Response:
    return Response(f"<Response><Message>{msg}</Message></Response>", media_type="application/xml")


@router.post("/whatsapp")
def whatsapp(
    From: str = Form(...),
    NumMedia: int = Form(0),
    MediaUrl0: str | None = Form(None),
    MediaContentType0: str | None = Form(None),
    db: Session = Depends(get_db),
):
    phone = From.replace("whatsapp:", "")
    patient = db.query(models.Patient).filter_by(phone=phone).first()
    if not patient:
        return _twiml("We could not match this number to a patient record. Please contact the clinic.")
    if NumMedia < 1 or not MediaUrl0:
        return _twiml("Please send a photo or PDF of your report.")

    ext = EXT_BY_MIME.get(MediaContentType0 or "", "")
    if not ext:
        return _twiml("Sorry, only photos (JPG/PNG) and PDFs are supported.")

    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    stored = Path(settings.upload_dir) / f"{uuid.uuid4().hex}{ext}"
    stored.write_bytes(download_media(MediaUrl0))
    doc = models.Document(patient_id=patient.id, filename=f"whatsapp{ext}", stored_path=str(stored), source="whatsapp")
    db.add(doc)
    db.commit()
    db.refresh(doc)
    process_document(db, doc)
    return _twiml("Thank you, your document has been added to your record.")
