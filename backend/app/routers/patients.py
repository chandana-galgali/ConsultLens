import json
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import models
from ..db import get_db
from ..services.briefing import patient_card, patient_out
from ..services.pipeline import reprocess_patient

router = APIRouter(prefix="/patients", tags=["patients"])


class PatientIn(BaseModel):
    name: str
    age: int | None = None
    mrn: str | None = None
    external_id: str | None = None
    phone: str | None = None
    blood_group: str | None = None
    lmp: date | None = None
    edd: date | None = None
    gravida: int | None = None
    para: int | None = None
    profile: dict | None = None


def _values(body: PatientIn, exclude_unset: bool = False) -> dict:
    data = body.model_dump(exclude_unset=exclude_unset)
    if "profile" in data:
        data["profile"] = json.dumps(data["profile"]) if data["profile"] else None
    return data


@router.post("")
def create_patient(body: PatientIn, db: Session = Depends(get_db)):
    p = models.Patient(**_values(body))
    db.add(p)
    db.commit()
    db.refresh(p)
    return patient_out(p)


@router.get("")
def list_patients(db: Session = Depends(get_db)):
    return [patient_card(db, p) for p in db.query(models.Patient).order_by(models.Patient.id).all()]


@router.get("/{pid}")
def get_patient(pid: int, db: Session = Depends(get_db)):
    p = db.get(models.Patient, pid)
    if not p:
        raise HTTPException(404, "Patient not found")
    return patient_out(p)


@router.patch("/{pid}")
def update_patient(pid: int, body: PatientIn, db: Session = Depends(get_db)):
    p = db.get(models.Patient, pid)
    if not p:
        raise HTTPException(404, "Patient not found")
    lmp_before = p.lmp
    for k, v in _values(body, exclude_unset=True).items():
        setattr(p, k, v)
    db.commit()
    if p.lmp != lmp_before:
        reprocess_patient(db, p)  # gestational ages depend on LMP
    db.refresh(p)
    return patient_out(p)
