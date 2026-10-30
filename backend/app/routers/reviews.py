"""Human evidence adjudication; no clinical recommendation is generated here."""
import json
from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.orm import Session

from .. import models
from ..db import get_db
from ..security import current_user, require_roles
from ..services.gap_checker import check_gaps

router = APIRouter(prefix="/reviews", tags=["evidence-review"])


class ReviewIn(BaseModel):
    target_type: Literal["observation", "checklist"]
    target_id: str = Field(min_length=1, max_length=100)
    decision: Literal["verified", "corrected", "unavailable", "clarification", "reviewed"]
    reason: str = Field(min_length=3, max_length=2000)
    corrected_value_num: float | None = None
    corrected_value_text: str | None = Field(default=None, max_length=200)

    @model_validator(mode="after")
    def validate_decision(self):
        if self.decision == "corrected":
            if self.target_type != "observation":
                raise ValueError("Only extracted observations can be corrected")
            if (self.corrected_value_num is None) == (self.corrected_value_text is None):
                raise ValueError("Supply exactly one corrected value")
        elif self.corrected_value_num is not None or self.corrected_value_text is not None:
            raise ValueError("Corrected values require the corrected decision")
        if self.target_type == "checklist" and self.decision in {"verified", "corrected"}:
            raise ValueError("Checklist status cannot be verified as a clinical fact")
        return self


def serialize(db: Session, entry: models.EvidenceReview) -> dict:
    reviewer = db.get(models.StaffUser, entry.reviewer_id)
    return {"id": entry.id, "patient_id": entry.patient_id, "target_type": entry.target_type,
            "target_id": entry.target_id, "decision": entry.decision, "reason": entry.reason,
            "document_id": entry.document_id, "reviewer": reviewer.email if reviewer else "unknown",
            "created_at": entry.created_at.isoformat(),
            "before": json.loads(entry.before_json) if entry.before_json else None,
            "after": json.loads(entry.after_json) if entry.after_json else None}


@router.get("/patients/{pid}")
def review_queue(pid: int, db: Session = Depends(get_db),
                 _user: models.StaffUser = Depends(current_user)):
    patient = db.get(models.Patient, pid)
    if not patient:
        raise HTTPException(404, "Patient not found")
    observations = db.query(models.Observation).filter_by(patient_id=pid).order_by(models.Observation.id).all()
    documents = {d.id: d for d in db.query(models.Document).filter_by(patient_id=pid).all()}
    checklist = check_gaps(db, patient).get("items", [])
    history = db.query(models.EvidenceReview).filter_by(patient_id=pid).order_by(models.EvidenceReview.id.desc()).all()
    latest = {}
    for item in history:
        latest.setdefault((item.target_type, item.target_id), serialize(db, item))
    return {
        "observations": [{"id": o.id, "label": o.label, "code": o.code,
            "value_num": o.value_num, "value_text": o.value_text, "unit": o.unit,
            "observed_on": o.observed_on.isoformat() if o.observed_on else None,
            "snippet": o.snippet, "document_id": o.document_id,
            "filename": documents[o.document_id].filename if o.document_id in documents else None,
            "verified": bool(o.verified), "review": latest.get(("observation", str(o.id)))}
            for o in observations if o.code != "plan"],
        "checklist": [{"id": str(item["id"]), "label": item.get("label", ""),
            "status": item.get("status", "unknown"),
            "review": latest.get(("checklist", str(item["id"]))) } for item in checklist],
        "history": [serialize(db, item) for item in history[:100]],
        "disclaimer": "Document availability and source verification only. No diagnosis, treatment or clinical scoring."
    }


@router.post("/patients/{pid}", status_code=201)
def adjudicate(pid: int, body: ReviewIn, db: Session = Depends(get_db),
               user: models.StaffUser = Depends(require_roles("doctor", "nurse", "lab"))):
    patient = db.get(models.Patient, pid)
    if patient is None:
        raise HTTPException(404, "Patient not found")
    if user.role == "lab" and body.target_type != "observation":
        raise HTTPException(403, "Lab role can review extracted observations only")
    observation = None
    before = after = None
    doc_id = None
    if body.target_type == "observation":
        if not body.target_id.isdecimal():
            raise HTTPException(422, "Invalid observation identifier")
        observation = db.get(models.Observation, int(body.target_id))
        if observation is None or observation.patient_id != pid:
            raise HTTPException(404, "Observation not found for patient")
        doc_id = observation.document_id
        before = {"value_num": observation.value_num, "value_text": observation.value_text,
                  "verified": bool(observation.verified)}
        if body.decision == "corrected":
            observation.value_num = body.corrected_value_num
            observation.value_text = body.corrected_value_text
            observation.verified = 1
            observation.edited = 1
        elif body.decision == "verified":
            observation.verified = 1
        elif body.decision in {"clarification", "unavailable"}:
            observation.verified = 0
        after = {"value_num": observation.value_num, "value_text": observation.value_text,
                 "verified": bool(observation.verified)}
    else:
        valid_ids = {str(item["id"]) for item in check_gaps(db, patient).get("items", [])}
        if body.target_id not in valid_ids:
            raise HTTPException(404, "Checklist entry not found")
    entry = models.EvidenceReview(patient_id=pid, target_type=body.target_type,
                                  target_id=body.target_id, decision=body.decision,
                                  reason=body.reason.strip(), reviewer_id=user.id,
                                  document_id=doc_id, before_json=json.dumps(before), after_json=json.dumps(after))
    db.add(entry)
    db.add(models.AuditEntry(actor_id=user.id, action=f"evidence_{body.decision}", patient_id=pid))
    db.commit()
    db.refresh(entry)
    return serialize(db, entry)
