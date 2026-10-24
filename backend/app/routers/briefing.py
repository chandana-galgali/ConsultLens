from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models
from ..db import get_db
from ..services.briefing import build_briefing

router = APIRouter(tags=["briefing"])


@router.get("/patients/{pid}/briefing")
def briefing(pid: int, narrative: bool = False, db: Session = Depends(get_db)):
    p = db.get(models.Patient, pid)
    if not p:
        raise HTTPException(404, "Patient not found")
    return build_briefing(db, p, narrative)


@router.get("/integrations/external/{external_id}/briefing")
def briefing_by_external(external_id: str, narrative: bool = False, db: Session = Depends(get_db)):
    """Used by the Care plugin: look up by the Care patient id."""
    p = db.query(models.Patient).filter_by(external_id=external_id).first()
    if not p:
        raise HTTPException(404, "No ConsultLens record linked to this external id")
    return build_briefing(db, p, narrative)
