"""Create first administrator from local environment; does not overwrite existing accounts."""
from app.config import settings
from app.db import Base, SessionLocal, engine
from app.models import StaffUser
from app.security import hash_password

if __name__ == "__main__":
    if not settings.jwt_secret or len(settings.jwt_secret) < 32:
        raise SystemExit("Set a strong JWT_SECRET (at least 32 characters) in backend/.env")
    if not settings.bootstrap_email or len(settings.bootstrap_password) < 12:
        raise SystemExit("Set BOOTSTRAP_EMAIL and BOOTSTRAP_PASSWORD (at least 12 characters)")
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.query(StaffUser).filter_by(email=settings.bootstrap_email.lower()).first():
            print("Administrator already present; no changes")
        else:
            db.add(StaffUser(email=settings.bootstrap_email.lower(), role="admin", password_hash=hash_password(settings.bootstrap_password)))
            db.commit()
            print("Administrator created:", settings.bootstrap_email.lower())
