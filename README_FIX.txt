ConsultLens v0.3 — login fix
==========================
Copy these files into the EXISTING consultlens project, preserving paths:
  backend/reset_admin.py                 NEW FILE
  frontend/src/styles.css              REPLACE FILE

1. In the backend terminal press Ctrl+C.
2. Make sure you are in consultlens/backend.
3. Run:
     .\.venv\Scripts\python.exe reset_admin.py
4. Enter the EXISTING admin email and choose a NEW unique password (12+ characters).
   The script updates only that existing administrator and does not delete patients.
5. Restart:
     .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
6. Reload the browser with Ctrl+Shift+R and log in using the email above and the new password.

If the reset script says no admin found:
  - Verify you are running it inside consultlens/backend.
  - Open backend/.env locally and check BOOTSTRAP_EMAIL and DATABASE_URL.
    Do not share .env contents or passwords.
  - From consultlens/backend, run:
      .\.venv\Scripts\python.exe bootstrap.py
    Then retry reset_admin.py.
  - If bootstrap reports an account already exists, the email typed in the reset tool
    must match an existing admin; inspect accounts locally without publishing data.

Note: the reset is LOCAL DEVELOPMENT ONLY, not a production account recovery system.
