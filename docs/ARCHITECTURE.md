# Architecture

```
 scanned PDF / photo / .txt / WhatsApp (later) / Care EMR
                     |
                     v
          +---------------------------+
          | FastAPI backend           |
          |  services/ocr.py          |  text from file (txt -> pdf text layer -> Tesseract/Textract)
          |  services/extraction.py   |  classify + dated values (regex, explainable)
          |  services/pipeline.py     |  glue + save
          |  services/timeline_builder|  events + previous-vs-latest (arithmetic only)
          |  services/gap_checker.py  |  expected items (YAML) vs record + quality flags
          |  services/summarizer.py   |  optional Claude rewording + interpretation guard
          +-------------+-------------+
                        | JSON  GET /patients/{id}/briefing
                        v
          +---------------------------+
          | React dashboard           |  frontend/  (same components reused in the Care plugin)
          +---------------------------+
```

## Design rules (these are the product)
1. **Retrieve, organise, highlight. Never interpret.** No normal/abnormal, no diagnosis, no advice.
2. **Provenance:** every value keeps its source document and the exact text line it was read from.
3. **Honest wording:** "not found in uploaded records", never "missed".
4. **Clinician-owned rules:** expected items live in `backend/app/rules/antenatal_schedule.yaml`.
5. **Claude is optional and fenced:** it only sees our structured JSON; an output guard rejects interpretive words.

## Data model
`Patient` (LMP, EDD, G/P, phone, external_id) -> `Document` (file, OCR text, type, date, source) -> `Observation`
(code, value, unit, date, gestation weeks, snippet).

## API
| Method | Path | Purpose |
|---|---|---|
| POST/GET/PATCH | `/patients`, `/patients/{id}` | create, list, update (changing LMP recomputes gestation weeks) |
| POST | `/patients/{id}/documents` | upload + OCR + extract |
| GET | `/documents/{id}/file`, `/documents/{id}/text` | original file, OCR text |
| GET | `/patients/{id}/briefing?narrative=true` | everything the dashboard needs |
| GET | `/integrations/external/{ext_id}/briefing` | lookup by Care patient id |
| POST | `/demo/seed` | synthetic demo patient |
| POST | `/webhooks/whatsapp` | Twilio WhatsApp ingestion (optional) |

## How the antenatal record maps to what is extracted today
(Dr. Gargi Pal's 3-page record was used as the field reference; it is not stored in this repo.)

| Section of the record | Status |
|---|---|
| Patient info: name, age, blood group, EDD, G/P | Stored on `Patient` (typed in, not OCR'd) |
| Menstrual history: LMP, EDD | LMP drives all gestational ages |
| 4. Investigations: Hb, platelets, F/PP sugar, HbA1c, TSH, creatinine | Extracted |
| 4. Investigations: CBC details, SGPT/SGOT, LFT, urine, HIV, HBsAg, HCV, VDRL | Not yet - add patterns to `LAB_PATTERNS` |
| 5. Special investigations (dual/triple/quad marker, TORCH, HPLC) | Not yet - add document types in `DOC_RULES` |
| 6. USG details: NT scan, Level II, growth, doppler | Document type detected; scan findings not parsed |
| 7. Clinical findings: weight, BP | Extracted (Hb, sugars as above); BMI not yet |
| 8. Immunisation: TT1, TT2, influenza | TT1/TT2/influenza extracted |
| 9. Notes / plan, handwriting | Needs Textract or a vision model; out of MVP scope |

## Extending (all small changes)
- **New lab value:** add one entry to `LAB_PATTERNS` + a test in `tests/test_extraction.py`.
- **New document type:** add to `DOC_RULES` + the label map in `frontend/src/components/Timeline.tsx`.
- **New expected item / change a window:** edit the YAML only.
