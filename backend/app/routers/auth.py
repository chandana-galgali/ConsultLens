from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .. import models
from ..db import get_db
from ..security import check_password, current_user, hash_password, require_roles, ROLES, token_for

router = APIRouter(prefix="/auth", tags=["authentication"])

class LoginIn(BaseModel):
    email: str
    password: str

class StaffIn(BaseModel):
    email: str
    password: str = Field(min_length=12)
    role: str

@router.post("/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.query(models.StaffUser).filter_by(email=body.email.strip().lower()).first()
    if user is None or not user.active or not check_password(body.password, user.password_hash):
        raise HTTPException(401, "Incorrect credentials")
    return {"access_token": token_for(user), "user": {"id": user.id, "email": user.email, "role": user.role}}

@router.get("/me")
def me(user: models.StaffUser = Depends(current_user)):
    return {"id": user.id, "email": user.email, "role": user.role}

@router.post("/staff", status_code=201)
def create_staff(body: StaffIn, user: models.StaffUser = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    if body.role not in ROLES:
        raise HTTPException(422, "Invalid role")
    email = body.email.strip().lower()
    if db.query(models.StaffUser).filter_by(email=email).first():
        raise HTTPException(409, "Account already exists")
    staff = models.StaffUser(email=email, password_hash=hash_password(body.password), role=body.role)
    db.add(staff); db.commit(); db.refresh(staff)
    return {"id": staff.id, "email": staff.email, "role": staff.role}
