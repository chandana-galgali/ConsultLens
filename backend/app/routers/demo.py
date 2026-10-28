from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..security import require_roles
from ..services.demo_data import create_demo_patients
from .. import models

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/seed")
def seed(db: Session = Depends(get_db), _user=Depends(require_roles("admin"))):
    """Creates three synthetic patients with realistic antenatal records.
    Idempotent — safe to call multiple times. Returns the first created (or existing) patient_id
    so the frontend can navigate directly to it."""
    created = create_demo_patients(db)

    # Return first created patient; if all existed already, return the first demo patient
    if created:
        first = created[0]
    else:
        first = db.query(models.Patient).filter_by(name="Priya Sharma").first()
        if not first:
            first = db.query(models.Patient).first()

    return {
        "message": f"Seeded {len(created)} patient(s).",
        "patient_id": first.id if first else None,
        "created_count": len(created),
    }
