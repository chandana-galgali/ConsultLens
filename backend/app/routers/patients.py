import json
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from .. import models
from ..db import get_db
from ..security import require_roles
from ..services.briefing import patient_card, patient_out
from ..services.pipeline import reprocess_patient

router = APIRouter(prefix="/patients", tags=["patients"])


class PatientIn(BaseModel):
    name: str
    age: int | None = None
    preferred_language: str = "en"
    reminder_opt_in: bool = False
    mrn: str | None = None
    external_id: str | None = None
    phone: str | None = None
    blood_group: str | None = None
    lmp: date | None = None
    edd: date | None = None
    gravida: int | None = None
    para: int | None = None
    profile: dict | None = None

    @field_validator("preferred_language")
    @classmethod
    def valid_language(cls, value: str) -> str:
        if value not in {"en", "hi", "mr"}:
            raise ValueError("Supported languages: en, hi, mr")
        return value

    @field_validator("phone")
    @classmethod
    def valid_phone(cls, value: str | None) -> str | None:
        if value and (not value.startswith("+") or not value[1:].isdigit() or not 8 <= len(value[1:]) <= 15):
            raise ValueError("Phone must be in international format e.g. +919876543210")
        return value


def _values(body: PatientIn, exclude_unset: bool = False) -> dict:
    data = body.model_dump(exclude_unset=exclude_unset)
    if "profile" in data:
        data["profile"] = json.dumps(data["profile"]) if data["profile"] else None
    return data


@router.post("")
def create_patient(body: PatientIn, db: Session = Depends(get_db), _user=Depends(require_roles("admin", "doctor", "nurse"))):
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
def update_patient(pid: int, body: PatientIn, db: Session = Depends(get_db), _user=Depends(require_roles("admin", "doctor", "nurse"))):
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
