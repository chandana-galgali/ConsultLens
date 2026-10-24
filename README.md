# ConsultLens

AI-assisted **pre-consultation briefing** for antenatal follow-ups. It gathers scattered records (scanned reports, PDFs,
photos, text), builds one chronological patient journey, shows previous-vs-latest values and **expected items not found
in uploaded records**, and flags record-quality problems. It retrieves and organises only - **the clinician interprets
and decides.**

- Track: Maternal & Women's Health - User: Doctor / Care team - Use case 02: Consultation Readiness & Patient Journey Review
- Stack: Python/FastAPI, Tesseract OCR (optional AWS Textract), rule-based extraction, SQLite/PostgreSQL, React + TypeScript,
  optional Claude API for wording only. Optional Care (OHC) plugin wrapper.

**Start with [START_HERE.md](START_HERE.md).**

Quick run:
```bash
cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000
cd frontend && npm install && npm run dev      # then click "Load demo patient"
```

## Intended user and workflow
An obstetrician or care team member opening a patient before a follow-up visit. Upload or sync records -> OCR and
extraction -> open the briefing -> review journey, trends, items not found, quality flags -> clinician decides.

## Safety principles
No diagnosis, no normal/abnormal labels, no treatment suggestions. Every value links to its source document and text.
Claude (optional) only rewords our structured data and its output is checked for interpretive language.
Synthetic data only.

## Known limitations
See [docs/LIMITATIONS.md](docs/LIMITATIONS.md). Architecture and extension points: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
