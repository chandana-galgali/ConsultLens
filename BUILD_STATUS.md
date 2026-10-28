# ConsultLens 0.3 — Incremental build status

## Implemented
- Existing FastAPI/React application retained (not a rewrite)
- JWT staff sign-in, scrypt password hashes, bootstrap admin and role gates on editing endpoints
- Review-required speech draft using the browser's Web Speech implementation where supported; typed fallback
- Immutable approved-note records with authorship and minimal audit event
- English/Hindi/Marathi interface language selection for capture; no automatic translation
- Patient messaging preference, opt-in check, and scheduled **mock** reminder queue
- More restrictive CORS, disabled unauthenticated WhatsApp webhook, capped upload size, generic parsing error
- Gestational-window match correction for documented checks; undated evidence doesn't satisfy a window
- Source provenance metadata for WHO and FOGSI reference catalogues
- Light hospital theme and login screen

## Not implemented — must not be represented as complete
- Real WhatsApp/SMS provider transmission or delivery receipts
- Robust streaming multilingual ASR, diarization or translation
- Clinically approved care-gap rules or clinical recommendation engine
- Production EMR / CARE authentication and encounter scope integration
- Background OCR queues, robust document malware scanning, comprehensive audit and tenant isolation
- Benchmark accuracy results or clinical validation
- Production-grade hospital deployment, backups, migrations and compliance reviews

## Local developer instructions
1. Requires Python 3.11+, Node 20+, Tesseract and Poppler for scanned PDFs.
2. `cd backend && python -m pip install -r requirements.txt`
3. From project root `python setup_local.py`; enter your own administrator email and password. The command creates the local `.env` and account.
4. Terminal A: `cd backend && uvicorn app.main:app --reload`
5. Terminal B: `cd frontend && npm ci && npm run dev`
6. Open `http://localhost:5173` and sign in. Use synthetic patients only. Admin can seed demo patients.
7. For additional staff, admin calls authenticated `POST /auth/staff` with email, 12+ character password and role `doctor`, `nurse`, `lab`, or `admin`.

**Deployment changes:** Existing Vercel/Render settings must be configured for a live authenticated backend (`JWT_SECRET`, admin bootstrap separately, `CORS_ORIGINS`, database). `VITE_API_URL` must point to the actual protected API. This archive is not automatically deployed by downloading it. Do not put secrets into frontend variables.

**Notes:** Browser dictation is browser-supported speech recognition, *not* an upload/recording pipeline, and browser providers may process audio remotely. Get explicit consent before any recording; synthetic demos only. The mock reminder cannot and will not send a patient notification.
