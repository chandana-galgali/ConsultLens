"""Password hashing, short-lived tokens and role-scoped authorization."""
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from . import models
from .config import settings
from .db import get_db

bearer = HTTPBearer(auto_error=False)
ROLES = {"admin", "doctor", "nurse", "lab"}


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    value = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"{salt.hex()}:{value.hex()}"


def check_password(password: str, stored: str) -> bool:
    try:
        salt, digest = stored.split(":", 1)
        calculated = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=2**14, r=8, p=1)
        return hmac.compare_digest(calculated, bytes.fromhex(digest))
    except (ValueError, TypeError):
        return False


def token_for(user: models.StaffUser) -> str:
    if not settings.jwt_secret:
        raise RuntimeError("JWT_SECRET must be configured")
    return jwt.encode({"sub": str(user.id), "role": user.role,
                       "exp": datetime.now(timezone.utc) + timedelta(hours=8)}, settings.jwt_secret, algorithm="HS256")


def current_user(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
                 db: Annotated[Session, Depends(get_db)]) -> models.StaffUser:
    if credentials is None or not settings.jwt_secret:
        raise HTTPException(401, "Authentication required")
    try:
        claims = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=["HS256"])
        uid = int(claims["sub"])
    except (jwt.PyJWTError, ValueError, KeyError):
        raise HTTPException(401, "Invalid or expired session") from None
    user = db.get(models.StaffUser, uid)
    if user is None or not user.active:
        raise HTTPException(401, "User unavailable")
    return user


def require_roles(*roles: str):
    def check(user: Annotated[models.StaffUser, Depends(current_user)]) -> models.StaffUser:
        if user.role not in roles:
            raise HTTPException(403, "Your role cannot perform this action")
        return user
    return check
