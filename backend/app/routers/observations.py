"""Deprecated direct edits: all corrections must create an audit entry."""
from fastapi import APIRouter, Depends, HTTPException
from ..security import require_roles

router = APIRouter(tags=["observations"])

@router.patch("/observations/{oid}")
def patch_observation(oid: int, _user=Depends(require_roles("doctor", "lab"))):
    raise HTTPException(410, "Direct edits are disabled. Use POST /reviews/patients/{patient_id} for audited corrections")
