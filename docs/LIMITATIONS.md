# Known limitations (state these openly in the submission and demo)

- **Synthetic data only.** Not validated on real patient records. No PHI-grade security, consent or audit logging.
- **Not a medical device.** It retrieves and organises; it does not diagnose, interpret or recommend.
- **Expected-item windows are placeholders** copied from the template's field labels. The treating clinician must
  confirm them (edit `antenatal_schedule.yaml`).
- **OCR:** Tesseract works well on clean printed text and poorly on handwriting and low-quality photos. AWS Textract
  is wired in behind `USE_TEXTRACT=true` but has not been run here.
- **Extraction is regex-based:** unusual layouts and units are missed; only the first match per parameter per document is
  taken. The spaCy step in the original submission is not implemented yet - the regex layer is the current NLP.
- **Dates are parsed day-first (dd/mm/yyyy).** Other formats are not read.
- **Claude summary is optional.** Without an API key a deterministic template summary is shown.
- **Care plugin:** scaffolded but not run inside a live Care instance (see `care-plugin/PORTING_PROMPT.md`).
- **WhatsApp ingestion** is implemented and covered by a mocked test only; not tried against live Twilio.
- **Paediatric / postnatal follow-up** mentioned in the submission is not built (no infant schedule yet).
- **Before any clinical use:** clinical validation, security and privacy review, consent, audit logs, NABH / Indian
  data-protection alignment.
