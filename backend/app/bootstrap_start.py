"""One-time, explicit administrator bootstrap for hosted deployments.

Set BOOTSTRAP_EMAIL and BOOTSTRAP_PASSWORD only for first deploy; remove afterwards.
"""
from .config import settings
from .db import Base, SessionLocal, engine
from .models import StaffUser
from .security import hash_password


def bootstrap_if_requested() -> None:
    if not (settings.bootstrap_email or settings.bootstrap_password):
        return
    if not settings.jwt_secret or len(settings.jwt_secret) < 32:
        raise RuntimeError("JWT_SECRET must have at least 32 characters")
    if not settings.bootstrap_email or len(settings.bootstrap_password) < 12:
        raise RuntimeError("Set both BOOTSTRAP_EMAIL and a BOOTSTRAP_PASSWORD of at least 12 characters")
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        email = settings.bootstrap_email.strip().lower()
        if db.query(StaffUser).filter_by(email=email).first() is None:
            db.add(StaffUser(email=email, role="admin", password_hash=hash_password(settings.bootstrap_password)))
            db.commit()
            print("Created administrator account for hosted environment")
        else:
            print("Administrator already exists; credentials unchanged")


if __name__ == "__main__":
    bootstrap_if_requested()
