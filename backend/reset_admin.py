"""Interactive local-development administrator credential recovery.

Run from the backend directory using the backend Python environment.
Requires existing local configuration and database access. Never expose as an HTTP endpoint.
"""
from __future__ import annotations

import getpass
from sqlalchemy import select

from app.db import Base, SessionLocal, engine
from app.models import StaffUser
from app.security import hash_password


def main() -> None:
    print("ConsultLens local administrator recovery (local development only).")
    email = input("Existing admin email: ").strip().lower()
    if not email or "@" not in email:
        raise SystemExit("Enter the existing administrator email address.")

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        user = db.scalar(select(StaffUser).where(StaffUser.email == email, StaffUser.role == "admin"))
        if user is None:
            raise SystemExit("No administrator with that email in the configured database. Check the backend/.env DATABASE_URL and original email.")
        password = getpass.getpass("New password (minimum 12 characters): ")
        confirm = getpass.getpass("Confirm new password: ")
        if len(password) < 12:
            raise SystemExit("Password must be at least 12 characters.")
        if password != confirm:
            raise SystemExit("Passwords do not match. Nothing was changed.")
        user.password_hash = hash_password(password)
        user.active = True
        db.commit()
    print("Administrator password updated. Log in using the email entered above.")


if __name__ == "__main__":
    main()
