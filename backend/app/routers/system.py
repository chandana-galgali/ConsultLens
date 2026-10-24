import shutil

import pytesseract
from fastapi import APIRouter

from ..config import settings
from ..services.gap_checker import load_rules

router = APIRouter(tags=["system"])


def _tesseract_version() -> str | None:
    try:
        return str(pytesseract.get_tesseract_version())
    except Exception:
        return None


@router.get("/system/status")
def status():
    """What is connected. Never returns keys or tokens, only whether they are set."""
    rules = load_rules()
    tess = _tesseract_version()
    return {
        "clinic": {"name": settings.clinic_name, "clinician": settings.clinician_name},
        "ocr": {
            "tesseract": {"available": tess is not None, "version": tess},
            "pdf_scans": {"available": shutil.which("pdftoppm") is not None or bool(settings.poppler_path)},
            "textract": {"enabled": settings.use_textract},
        },
        "ai": {"claude": {"configured": bool(settings.anthropic_api_key), "model": settings.claude_model}},
        "channels": {
            "whatsapp": {"configured": bool(settings.twilio_account_sid and settings.twilio_auth_token)},
            "care": {"configured": bool(settings.care_base_url and settings.care_token), "base_url": settings.care_base_url},
        },
        "database": {"engine": "postgresql" if settings.database_url.startswith("postgres") else "sqlite"},
        "rules": {"version": rules["version"], "note": rules["note"], "count": len(rules["expected"])},
    }


@router.get("/rules")
def rules():
    """The clinic-owned schedule of expected items (read-only here; edit rules/antenatal_schedule.yaml)."""
    return load_rules()
