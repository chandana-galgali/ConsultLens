"""Run once: python setup_local.py. Creates local-only credentials and bootstraps admin."""
import getpass
import secrets
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
file = root / "backend" / ".env"
if file.exists():
    print("backend/.env already exists; preserving it.")
else:
    print("ConsultLens local configuration. Use synthetic patient records only.")
    email = input("Admin email: ").strip().lower()
    password = getpass.getpass("Admin password (12+ characters): ")
    if not email or "@" not in email or len(password) < 12:
        raise SystemExit("Valid admin email and password of at least 12 characters are required")
    content = f"JWT_SECRET={secrets.token_urlsafe(48)}\nBOOTSTRAP_EMAIL={email}\nBOOTSTRAP_PASSWORD={password}\nDATABASE_URL=sqlite:///./consultlens.db\nCORS_ORIGINS=[\"http://localhost:5173\",\"http://127.0.0.1:5173\"]\n"
    file.write_text(content)
    try: file.chmod(0o600)
    except OSError: pass
    print("Created backend/.env locally (do not commit).")
subprocess.run([sys.executable, "bootstrap.py"], cwd=root / "backend", check=True)
print("Now run: cd backend && uvicorn app.main:app --reload")
print("In another terminal: cd frontend && npm ci && npm run dev")
