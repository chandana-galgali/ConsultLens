<div align="center">

# ConsultLens

### Verified patient journeys. More prepared consultations.

**An AI-assisted, multilingual consultation-readiness and care-coordination workspace for fragmented healthcare records.**

[Live Demo](https://consultlens.vercel.app/) · [Source Code](https://github.com/chandana-galgali/ConsultLens) · [Report an Issue](https://github.com/chandana-galgali/ConsultLens/issues)

**Health-a-thon 2026** · **Maternal & Women's Health** · **Use Case 02: Consultation Readiness & Patient Journey Review**

</div>

> [!IMPORTANT]
> **Hackathon prototype — synthetic data only.** ConsultLens is not a diagnostic system, medical device, treatment recommender, or clinically validated decision-support product. Documentation checks are not clinical risk scores. Clinicians remain responsible for reviewing source records and making all clinical decisions.

## The problem

Relevant patient information often lives across scanned reports, laboratory results, ultrasound documents, prescriptions, consultation notes, and separate hospital systems. Before a follow-up appointment, clinicians may need to reconstruct the patient's history manually, reconcile conflicting details, and search for missing paperwork.

**ConsultLens makes the existing records easier to find, understand, verify, and act on as a team.** The initial workflow focuses on antenatal follow-up consultations, with an architecture intended to support other specialties later.

## What ConsultLens does

```text
PDFs / scans / photos / text / staff documentation
                     │
                     ▼
          OCR + information extraction
                     │
                     ▼
         Structured patient record
                     │
       ┌─────────────┼──────────────┐
       ▼             ▼              ▼
  Patient journey  Record checks  Evidence review
       │             │              │
       └─────────────┼──────────────┘
                     ▼
     Source-linked consultation briefing
                     │
                     ▼
       Clinician review and approval
                     │
                     ▼
       Notes + coordinated follow-up
```

### Implemented in the current source (v0.6)

| Capability | Description |
| --- | --- |
| **Patient workspace** | Patient registration, longitudinal journey, records, investigations, trends and documentation views. |
| **Document ingestion** | Upload PDFs, images and supported text records; OCR and rule-based extraction organize the content. |
| **Consultation briefing** | Generates a structured pre-consultation summary from available records; optional AI-assisted wording. |
| **Evidence Review Queue** | Authorized staff can verify, correct, mark unavailable, or request clarification on extracted information, with persistent reviewer history. |
| **Human-reviewed notes** | Typed notes, browser-dependent dictation, and approved documentation stored with the patient. |
| **Recorded-audio drafts** | Optional server-side transcription of synthetic/consented audio when an AI API key is configured; requires human review before saving. |
| **Multilingual workflow** | English, Hindi and Marathi options for supported dictation and reminder templates; full clinical translation is not implemented. |
| **Staff sign-in** | Administrator, doctor, nurse and laboratory roles with server-side role checks for selected actions. |
| **Reminder coordination** | Consent-gated appointment reminders saved to a **mock queue**; **no WhatsApp/SMS delivery** in this version. |
| **Interface** | Light/dark theme, patient-centric tabs, dedicated care workspace and evidence review controls. |

### Not yet complete

- Automatic LLM claim-by-claim evidence grading and benchmarked extraction accuracy.
- Production-grade multilingual translation, speaker diarization and clinical terminology verification.
- Live WhatsApp/SMS delivery, approved messaging templates and a reliable dispatch worker.
- Verified live integration with Open Healthcare Network's CARE EMR (the repository includes a scaffold).
- Clinician-approved antenatal rules, cross-facility patient authorization, full security/privacy assessment and clinical validation.

**Do not confuse an implemented interface or API scaffold with a clinically approved or externally verified integration.**

## Technology

| Layer | Stack |
| --- | --- |
| Frontend | React 18, TypeScript, Vite |
| Backend API | Python, FastAPI, Pydantic |
| Persistence | SQLAlchemy; SQLite locally, PostgreSQL for hosted deployment |
| Document processing | Tesseract OCR, PDF extraction, rule-based field extraction; optional Textract |
| AI services | Optional Anthropic wording and OpenAI audio transcription |
| Object storage | Local uploads for development; optional S3-compatible storage |
| Hosting | Vercel (frontend), Render (backend and PostgreSQL) |
| Interoperability | Preliminary CARE frontend/backend plugin scaffold |

## Local development

**Requirements:** Python **3.12** (recommended for this project's tested environment), Node.js with npm, and Git. Install Tesseract OCR for scanned images; Poppler is additionally required for scanned-PDF rendering on Windows. Pure text documents may not require these external tools.

### 1. Clone

```bash
git clone https://github.com/chandana-galgali/ConsultLens.git
cd ConsultLens
```

### 2. Install backend dependencies

**Windows PowerShell** (from the repository root):

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
cd ..
```

**macOS/Linux:**

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cd ..
```

### 3. Create the first local administrator

From the **repository root**, run either:

```powershell
# Windows
.\backend\.venv\Scripts\python.exe setup_local.py
```

```bash
# macOS/Linux, using the backend virtual environment
backend/.venv/bin/python setup_local.py
```

The setup prompts you for an administrator email and a **new, unique password of at least 12 characters**, creates `backend/.env`, and bootstraps the local account. An email ending in `.local` can be used for a fictional demo account; no email verification is performed.

**Important:** The bootstrap is create-only. Running it again does **not** change the password of an existing administrator. Never delete a database just to reset a password.

### 4. Run the backend

```powershell
# Windows, from repository root
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

```bash
# macOS/Linux, from repository root
cd backend
.venv/bin/python -m uvicorn app.main:app --reload
```

Backend health: **http://127.0.0.1:8000/health**

### 5. Run the frontend

Open a **second terminal** in the repository root:

```bash
cd frontend
npm ci
npm run dev
```

Open **http://localhost:5173** and sign in with the local administrator credentials. Use the admin-only demo seed action to load three synthetic antenatal journeys, then create other staff accounts through the team-management UI.

> [!NOTE]
> The Vite development proxy sends API paths to `http://localhost:8000`. The production Vercel deployment does not use that proxy; it needs `VITE_API_URL` configured separately.

## Demo walkthrough

1. **Sign in as administrator.** Create doctor, nurse and lab staff demo accounts, using **different passwords** for each.
2. **Load synthetic demo patients.** Open the patient list and select a journey.
3. **Review the patient story.** Navigate the Overview, investigations, timeline, document and trend views; read the generated briefing.
4. **Inspect source evidence.** Select an extracted observation, open the evidence review interface, and consult its linked source where available.
5. **Make a documented decision.** Verify an observation, correct a value with a reason, or request clarification. Refresh and check the review history.
6. **Create a note.** In Care workspace, type or dictate a note. Review its contents before saving. Optional server-side transcription uses synthetic audio only.
7. **Coordinate follow-up.** Set fictional contact details and explicit messaging opt-in; schedule a multilingual **mock** reminder. It is not actually sent.
8. **Switch roles.** Check which operations a doctor, nurse, lab staff member and administrator can perform.

The documentation checklist identifies information **not found in supplied records**, which is not equivalent to proof that a clinical investigation was not performed.

## Run checks

From the repository root:

```powershell
# Windows backend tests
cd backend
.\.venv\Scripts\python.exe -m pytest -q
```

```bash
# Frontend production build (from frontend/)
npm ci
npm run build
```

Benchmark utilities are under `evaluation/`; they do **not** establish validated accuracy or superiority over competing systems without an independently labeled test dataset. See `TEST_PLAN_v0.6.md` if that file is retained in your checkout.

## Deployment: Render + Vercel

**The local and hosted environments do not share accounts or databases automatically.** Create demo-only hosted accounts independently. Never commit `.env`, databases, uploads, API keys, or credentials.

### Render — backend and database

1. Deploy the GitHub repository to a Render Python web service with **Root Directory `backend`** (matching the existing `backend/render.yaml`).
2. Provision Render PostgreSQL in the **same region** as the web service. Use its **internal** database URL for `DATABASE_URL`. Prefer a persistence plan suitable for the demo; free database services may expire.
3. Configure the following **server-side environment variables**:

   | Variable | Value / purpose |
   | --- | --- |
   | `DATABASE_URL` | Render PostgreSQL internal URL (secret) |
   | `JWT_SECRET` | Unique random secret of at least 32 characters |
   | `CORS_ORIGINS` | `["https://consultlens.vercel.app"]` (JSON array of trusted origins) |
   | `MESSAGE_PROVIDER` | `mock` — current version does not dispatch real messages |
   | `PYTHON_VERSION` | `3.12.9` as configured in `backend/render.yaml` |
   | `BOOTSTRAP_EMAIL` | Temporary first-deploy admin identity |
   | `BOOTSTRAP_PASSWORD` | Temporary, unique 12+ character bootstrap password |

4. Build command:

   ```bash
   pip install -r requirements.txt
   ```

5. Start command:

   ```bash
   python -m app.bootstrap_start && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

6. Deploy and check `https://YOUR-RENDER-HOST/health`. Sign in successfully with the hosted admin, then **remove** `BOOTSTRAP_EMAIL` and `BOOTSTRAP_PASSWORD` from Render and redeploy. The bootstrap will not reset an account that already exists.
7. Create doctor, nurse and lab demo accounts using the admin UI. The laboratory account's internal role is **`lab`**, even if the display name is “lab staff.”

**Files are separate from database records.** For uploaded PDFs/images to survive Render redeploys, configure private S3-compatible object storage via `S3_BUCKET`, `AWS_REGION`, appropriate server-side credentials, and optionally `S3_ENDPOINT_URL`. Without this, Render's ephemeral filesystem can lose uploaded documents. Historical local files are not migrated automatically.

### Vercel — frontend

1. Connect the same repository; use **Root Directory `frontend`**.
2. Use `npm ci` to install, `npm run build` to build, and `dist` as the output directory.
3. Set `VITE_API_URL` to your Render **HTTPS base URL**, without a trailing slash or path suffix.
4. Redeploy the frontend after changing the environment variable.
5. Open [consultlens.vercel.app](https://consultlens.vercel.app/) and verify that browser login and `/reviews/...` network requests target **Render**, not Vercel or localhost.

Only the live deployed environment's configured database determines which accounts and patient records exist there.

## Optional integrations

| Environment setting | Enables | If absent |
| --- | --- | --- |
| `OPENAI_API_KEY` | Synthetic recorded-audio transcription (`AUDIO_TRANSCRIPTION_MODEL` controls model) | Transcription endpoint returns an unavailable/configuration error; manual notes remain usable |
| `ANTHROPIC_API_KEY` | Optional AI-assisted summary wording | Structured/deterministic summary remains available |
| `USE_TEXTRACT` + AWS configuration | Optional AWS OCR path | Local OCR pipeline is used |
| `S3_BUCKET` + storage credentials | Durable document storage | Local filesystem upload storage |
| `CARE_BASE_URL` / `CARE_TOKEN` | Integration configuration inputs | CARE integration is not live or verified |

Do not put server-side secrets in variables prefixed with `VITE_`: those are embedded into the browser build.

## Repository structure

```text
backend/          FastAPI routes, security, services, rules, tests, Render config
frontend/         React UI, state, API adapters, themes, Vite config
care-plugin/      Preliminary Open Healthcare Network CARE plugin scaffold
evaluation/       Offline extraction scoring utilities and input format
sample_data/      Synthetic document examples
docs/             Architecture and known limitations
setup_local.py    Interactive local administrator/bootstrap setup
```

## Safety, privacy and clinical governance

- **Only synthetic/de-identified demonstration material** should be used; do not upload real patient records or recordings.
- The antenatal YAML documentation schedule is **not clinician-approved**. Missing/available record labels must not be presented as treatment guidance, clinical negligence findings, or a diagnosis.
- OCR, extraction, automated summarization and transcription can be wrong. Clinician review and original-source inspection are necessary.
- Role-based checks exist for selected operations, but facility-scoped patient access, enterprise-grade identity, immutable audit controls and a full security review remain outstanding.
- This prototype has not undergone clinical effectiveness studies or independent regulatory validation.

For the design context and limitations, see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) and [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md).

## Project direction

Our long-term goal is a **verifiable, multilingual intelligence layer** that sits alongside existing EMRs: reconstructing patient journeys, preserving original evidence, supporting clinician adjudication, and measuring reliability on professionally reviewed datasets. Advanced clinical-rule interpretation will require formal approval and validation before use.

---

<div align="center">

**ConsultLens — Evidence first. Clinicians in control.**

Built for **Health-a-thon 2026 · Maternal & Women's Health**

</div>
