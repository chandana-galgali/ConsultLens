from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import models

from ..db import get_db

router = APIRouter(tags=["observations"])


class ObservationPatch(BaseModel):
    value_num: float | None = None
    value_text: str | None = None
    verified: bool | None = None


@router.patch("/observations/{oid}")
def patch_observation(oid: int, body: ObservationPatch, db: Session = Depends(get_db)):
    """Clinician confirms an extracted value against the original, or corrects it."""
    o = db.get(models.Observation, oid)
    if not o:
        raise HTTPException(404, "Value not found")
    changes = body.model_dump(exclude_unset=True)
    if "value_num" in changes:
        o.value_num, o.edited, o.verified = changes["value_num"], 1, 1
    if "value_text" in changes:
        o.value_text, o.edited, o.verified = changes["value_text"], 1, 1
    if "verified" in changes and changes["verified"] is not None:
        o.verified = 1 if changes["verified"] else 0
    db.commit()
    return {"id": o.id, "verified": bool(o.verified), "edited": bool(o.edited),
            "value": o.value_num if o.value_num is not None else o.value_text}
