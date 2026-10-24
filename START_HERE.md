# START HERE: build, run and understand ConsultLens (step by step)

Read this top to bottom once. Every step says **what** we are doing, **why**, the **command**, and **what you should see**.

---

## 0. What you are building (one paragraph)

A doctor opens ConsultLens before a follow-up visit and sees, on one screen: the patient's journey in date order, the previous vs latest value of each lab or vital, a list of **expected items not found in uploaded records**, and **record-quality flags** (missing dates, conflicting values, EDD mismatch). Every number links back to the scan it came from. The software **retrieves and organises; the doctor interprets and decides.** It never says normal/abnormal, never diagnoses, never advises.

**Approach in one line:** build a small pipeline that works with no AI service at all (OCR -> rules -> database -> dashboard), then add Claude only for wording the summary, so the demo never depends on an API key or the internet.

### Status of this code (be honest with yourself)
| What | Status |
|---|---|
| Python syntax of all backend files | Checked |
| OCR (real Tesseract) on the 5 synthetic "scans" -> classification -> value extraction -> timeline -> trends -> expected-item gaps -> template summary | **Ran and gave the expected output** (using the real project code in an offline harness) |
| FastAPI server, `pytest` suite, React app build, Docker, Care plugin | **Not run yet** (the sandbox I built this in cannot download packages). Expect to fix a small thing or two on first run. Section 12 lists likely ones |

---

## 1. Install the tools (once)

**What/why:** Python runs the backend, Node runs the frontend, and **Tesseract** is the OCR program the Python code calls. Without Tesseract installed, uploading an image fails.

| You need | Check with | Version |
|---|---|---|
| Python | `python3 --version` (Windows: `python --version`) | 3.11 or newer |
| Node.js + npm | `node -v` | 18 or newer |
| Tesseract OCR | `tesseract --version` | any 5.x |
| Poppler (only to read *scanned PDFs*) | `pdftoppm -v` | any |
| Git (for Care later) | `git --version` | any |

- **Windows (easiest):** install WSL2 + Ubuntu (`wsl --install` in PowerShell, restart), then follow the Ubuntu line below inside Ubuntu.
  Native Windows also works: install Python, Node, the "UB Mannheim" Tesseract build, and Poppler for Windows, and add them to PATH.
- **Ubuntu / WSL:** `sudo apt update && sudo apt install -y tesseract-ocr poppler-utils python3-venv python3-pip nodejs npm`
- **macOS:** `brew install python tesseract poppler node`

**You should see:** each check command prints a version number.

---

## 2. Run the backend

**What/why:** the backend is the brain: OCR, extraction, database, expected-item rules. We use a *virtual environment* so its packages do not clash with other projects, and SQLite so there is nothing to set up (PostgreSQL later via Docker).

```bash
cd consultlens/backend
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**You should see:** `Uvicorn running on http://127.0.0.1:8000`. Open **http://localhost:8000/docs** - an interactive page listing every API endpoint. Open `http://localhost:8000/health` -> `{"status":"ok"}`.
Leave this terminal running.

---

## 3. Run the frontend

**What/why:** the React dashboard the doctor sees. It only talks to the backend over HTTP.

Open a **second terminal**:
```bash
cd consultlens/frontend
npm install
npm run dev
```
**You should see:** `Local: http://localhost:5173/`. Open it.

---

## 4. See it work (the 60-second demo)

1. In the page click **Load demo patient**. (Behind the scenes the backend draws 5 fake "scanned" reports as images, runs real OCR on them, and fills the database.)
2. You should see "Asha Demo, GA 26+0" and:
   - **Expected items vs record:** *Not found in uploaded records:* Level II scan (18 to 22 wks); *Window open, not found yet:* TT2 vaccine, Blood sugar (24 to 28 wks). Found items are tucked under "Found / upcoming".
   - **Previous vs latest:** Hemoglobin 10.4 -> 9.6 (change -0.8), BP systolic 118 -> 132, weight 62 -> 66. Click any value: the original scan opens (this is the provenance feature).
   - **Patient journey:** 5 documents in date order with gestational age at each (8+0, 12+0, 14+0, 20+0, 25+0).
   - A short summary sentence at the top (template, unless you add a Claude key).
3. Try **+ Add reports** and upload files from `sample_data/` (create a *New patient* with LMP **2026-04-15** first). Try a `.txt` and a `.png` - same result, proving the pipeline handles different formats.

---

## 5. Run the tests

**What/why:** extraction is where silent mistakes hide (a regex reading "HbA1c 5.4" as Hb). Tests catch that before the demo.
```bash
cd consultlens/backend
source .venv/bin/activate
PYTHONPATH=. pytest -q
```
**You should see:** all tests passing (one real-OCR test is skipped automatically if Tesseract is missing). If any fail, read the failure - they are written to be readable - and fix the one line.

---

## 6. Tour of the code (in the order data flows)

Open each file while you read; every file is short and commented.

| # | File | What it does | Approach / why |
|---|---|---|---|
| 1 | `backend/app/config.py` | Settings from `.env` | One place for keys and switches |
| 2 | `backend/app/models.py` | 3 tables: Patient, Document, Observation | An *Observation* stores value + date + gestational age + **the exact text line it came from** (provenance) |
| 3 | `backend/app/services/ocr.py` | File -> text | Cheapest method first: .txt, then PDF text layer, then Tesseract (Textract optional) |
| 4 | `backend/app/services/extraction.py` | Text -> document type, date, values | Plain regex: predictable and explainable to judges. Dates read day-first (dd/mm/yyyy) |
| 5 | `backend/app/services/pipeline.py` | Runs 3 + 4 and saves | One function, `process_document` |
| 6 | `backend/app/services/timeline_builder.py` | Events in date order; previous vs latest | "Change" is subtraction only - never a verdict |
| 7 | `backend/app/rules/antenatal_schedule.yaml` | What is *expected* and when | Doctor-editable. **Windows are placeholders - get Dr. Pal to confirm** |
| 8 | `backend/app/services/gap_checker.py` | Expected vs found + quality flags | Wording is "not found in uploaded records", never "missed" |
| 9 | `backend/app/services/summarizer.py` | Short narrative | Claude sees only our JSON; a guard rejects words like "low/abnormal/suggests" and falls back to the template |
| 10 | `backend/app/routers/*.py` | The HTTP endpoints | Thin: validate, call a service, return JSON |
| 11 | `frontend/src/api.ts` | All calls to the backend | Base URL is configurable so the same code runs inside Care |
| 12 | `frontend/src/components/*.tsx` | Dashboard pieces | `BriefingView` = the whole briefing; reused by the Care plugin |
| 13 | `backend/tests/` | Safety net | Includes the interpretation-guard test |

### Project structure
```
consultlens/
├── START_HERE.md            <- this file
├── README.md
├── docker-compose.yml       API + PostgreSQL in one command (optional)
├── sample_data/             synthetic reports (png + txt) for upload practice
├── docs/                    ARCHITECTURE.md, LIMITATIONS.md
├── backend/
│   ├── requirements.txt, Dockerfile, .env.example
│   ├── app/  main.py config.py db.py models.py
│   │   ├── routers/   patients.py documents.py briefing.py demo.py whatsapp.py
│   │   ├── services/  ocr.py extraction.py pipeline.py timeline_builder.py gap_checker.py summarizer.py demo_data.py
│   │   └── rules/     antenatal_schedule.yaml
│   ├── seed/          make_synthetic_data.py  make_sample_files.py
│   └── tests/         conftest.py test_extraction.py test_api.py
├── frontend/          package.json vite.config.ts index.html src/{App,api,types,main}.tsx(ts) src/components/*
└── care-plugin/       PORTING_PROMPT.md, backend/care_consultlens/*, frontend/src/*
```

---

## 7. Make it yours (small, safe changes)

| I want to... | Change this | Then |
|---|---|---|
| Change when an item is expected | `backend/app/rules/antenatal_schedule.yaml` | Refresh the page |
| Extract a new lab (e.g. SGPT, HIV) | Add one line to `LAB_PATTERNS` in `extraction.py` | Add a test in `test_extraction.py` |
| Recognise a new document type | Add a line to `DOC_RULES`, and a label in `Timeline.tsx` | Add a test |
| Turn on Claude wording | Copy `backend/.env.example` to `backend/.env`, set `ANTHROPIC_API_KEY=...`, restart backend | Summary line shows the model name instead of "template" |
| Better OCR for handwriting | Set `USE_TEXTRACT=true` + AWS credentials | Test on a handwritten sample first |

**Use only synthetic data with the Claude API** - never real patient records.

---

## 8. Build in this order (the plan)

You said you have time. Suggested order; stop adding features at the end of Day 5.

| Day | Goal | Done when |
|---|---|---|
| 1 | Sections 1-4: run everything, click the demo | You can explain each panel |
| 2 | Section 5-6: read the code, run tests, add 2 lab patterns from the antenatal record (SGPT, HIV) | Tests pass with your additions |
| 3 | Show Dr. Pal the YAML + dashboard; get the expected-item windows confirmed | `rules_note` updated to "confirmed by Dr. Pal" |
| 4 | Upload *your own synthetic* scans (phone photos of printed fake reports) and fix what OCR misses | A messy photo still works |
| 5 | Care: Section 9 | Hello-world plugin visible in Care |
| 6 | Embed ConsultLens in Care, or fall back to a slide | Demo path chosen and rehearsed |
| 7 | README, limitations, demo video, rehearse | Nothing new gets built |

---

## 9. Building on CARE (the Open Healthcare Network part)

**What I read** (your email's links): the Plugin docs, the `care_scaffold`, `care_ai_vision_fe`, `care_filly`, the OHC skills repo and the cookiecutter. Key facts:
- A Care plugin has a **backend** (Django app, registered in `plug_config.py`, served at `/api/<plugin-name>/`) and/or a **frontend** (React bundle loaded through Vite module federation, described by a `manifest.tsx`).
- `care_filly` (backend) keeps its service secret **on the server** and reuses Care's own JWT login; `care_ai_vision_fe` (frontend) is the one that reads scanned forms inside Care. Our plugin follows the same split: a thin Django proxy + a React page.
- `care_scaffold` is built so that **an AI coding agent sets everything up** from one instruction: `Read and execute ./bootstrap.prompt.md`. It clones Care, starts Docker services and creates plugin repos without touching Care core. Needs Git, Node, Python 3, Docker + Compose.

**Our approach (two phases, so you are never stuck):**
1. Phase A (Days 1-4): the standalone app you just ran. This is your guaranteed demo.
2. Phase B (Days 5-6): embed the same React components in Care and put a small Django proxy in front of the FastAPI service.

**Steps:**
1. Watch the Loom walkthrough and skim https://docs.ohc.network/contributing/plugins/.
2. `git clone https://github.com/ohcnetwork/care_scaffold.git` and open Claude Code in it.
3. Send: `Read and execute ./bootstrap.prompt.md` and answer its questions using the brief in **`care-plugin/PORTING_PROMPT.md`** (it is ready to paste and tells the agent exactly which of our files to copy).
4. Optional: install the OHC skills (`git clone https://github.com/ohcnetwork/skills`, then symlink the skill folders into `~/.claude/skills/`) - useful ones: `care-review`, `playwright`.
5. Run your ConsultLens API on the host (port 8000), set `CONSULTLENS_API_URL` for the plugin (see `plug_config_snippet.py`), open a patient in Care.

**Be honest about:** the route format, the patient-page extension slot and how to read the patient id/token are things I could **not** verify (they live in `care_fe` and the scaffold, not in the pages I could read). `PORTING_PROMPT.md` has a verified-vs-unverified table. Tell the judges exactly that.

---

## 10. Optional: PostgreSQL + Docker (matches your submitted stack)
```bash
cd consultlens
docker compose up --build        # API on :8000 with PostgreSQL
# frontend still: cd frontend && npm run dev
```
Then `curl -X POST localhost:8000/demo/seed` or use the button.

---

## 11. Demo script (3 minutes) and what to say

1. "Before every follow-up, the doctor rebuilds the story from scattered scans." Show `sample_data/` - mixed photos, PDFs, text.
2. Upload them (OCR runs live). "Different formats, one timeline."
3. Point at the three panels. "Previous vs latest, expected items not found, record quality."
4. Click a value -> the original scan opens. "Every number is traceable."
5. Point at "not found in uploaded records". "It does not say missed or abnormal. The doctor decides."
6. Open `antenatal_schedule.yaml`, change a window, refresh. "The clinic owns the rules."
7. (If done) Show it inside Care.
8. Stopwatch line: "From opening the patient to a full picture: under a minute." **Time it for real** - the mentor brief's ROI figures (150 hours/day etc.) are illustrative assumptions, not measurements. Use your measured number.

---

## 12. Troubleshooting (likely first-run issues)

| Symptom | Fix |
|---|---|
| `TesseractNotFoundError` | Tesseract not installed / not on PATH (Section 1). Windows: add its folder to PATH or set `pytesseract.pytesseract.tesseract_cmd` in `ocr.py` |
| Upload of a scanned PDF fails with `pdftoppm` / Poppler error | Install Poppler (Section 1) |
| Dashboard says "Cannot reach the API" | Backend not running on port 8000, or a different frontend port: add it to `CORS_ORIGINS` in `.env` |
| `pip install` fails on `psycopg[binary]` | You do not need it for SQLite: delete that line from `requirements.txt` (keep it for Docker/PostgreSQL) |
| OCR reads a value wrong | Open `/documents/{id}/text` to see the raw OCR text, then adjust the pattern in `extraction.py` |
| Everything shows "GA ?" | The patient has no LMP: type it in the banner on the page |
| Port already in use | `uvicorn ... --port 8001` and set `VITE_API_URL=http://localhost:8001` before `npm run dev` |
| `npm install` TypeScript errors on `npm run typecheck` | Run `npm run dev` / `npm run build` first; send me the exact message and I will fix it |

---

## 13. Extra suggestions (worth considering)

1. **Show OCR confidence and a "Check this" tag.** `care_ai_vision_fe` marks low-confidence lab values "Check this" (default threshold 0.99). Tesseract gives per-word confidence (`image_to_data`); store it on each Observation. Strong trust feature.
2. **Let the clinician confirm or correct a value.** One "confirm / edit" click per extracted number, with who and when. This is the human-in-the-loop story judges look for.
3. **Handwriting:** compare Textract against sending the page image to a vision-capable Claude *only for structuring into fields* (keep the snippet). Test both on synthetic handwritten pages.
4. **Cover "gather additional context":** the use-case text says clinicians should be able to gather more context. A "Request missing report" button that sends the patient a WhatsApp message (admin action, not clinical advice) fits this and your Twilio plan.
5. **Postnatal / paediatric:** your submission mentions it. Add a second YAML (`infant_immunisation.yaml`) and a `Patient.dob` later; the gap-checker code does not change.
6. **Mentor's GPT brief:** it also proposes guideline evidence links and a hospital ROI pilot. I kept those out of the build on purpose; use them as roadmap slides, labelled as proposals.
7. **Privacy habit:** the Antenatal Record template is a real clinic's document. Keep it for reference, never commit it with a patient's details, and never paste real records into any AI tool.
