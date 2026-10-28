# ConsultLens v0.4 — UI and gestational-age maintenance release

## Apply the simplest way (Windows)
1. Stop the Vite frontend (Ctrl+C); stop the FastAPI backend (Ctrl+C).
2. Back up your `consultlens` folder or commit your current changes.
3. Extract **ConsultLens_v0.4_Changed_Files.zip**. Copy its `frontend` and `backend` directories into your existing `consultlens` folder; choose *Replace files*.
4. In `consultlens/frontend`: `npm ci` then `npm run dev`.
5. In `consultlens/backend`: `.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload`.
6. Open `http://localhost:5173` and use Ctrl+Shift+R to discard cached CSS.

The changed-files patch preserves your **existing users, passwords, and patient database**. Never delete the `consultlens.db` database to apply a UI update.

## What changed
- Backend `build_briefing` now includes a date-derived gestational-age field, based on recorded LMP, rather than requiring the nonexistent `snapshot.ga` field.
- Frontend maps that field and has a local date-derived compatibility fallback. If LMP is unavailable, the UI explicitly says `GA unavailable`.
- Removed conflicting late theme CSS definitions, introducing consistent light/dark token sets.
- Added a persistent light/dark theme switch in the sidebar (preference retained in local browser storage).
- VoiceBridge is now a collapsible **in-page** section, closed initially. It no longer dominates every record view.
- Improved contrast for notes, controls, labels, selected tabs, input placeholders, login screen, and form fields.
- Added mobile and tablet responsive treatment for the patient selector, navigation tabs, record panels, and VoiceBridge.
- Re-fetches a fresh briefing on refresh instead of reusing the cached one.

## Test checklist
- Desktop: select each demo patient, move among Overview/Investigations/Documents. VoiceBridge must remain hidden until explicitly opened. Confirm document panels are usable without overlay.
- GA: check LMP-based `GA weeks+days` in sidebar and patient header. If there is no LMP, `GA unavailable` is correct; **do not fabricate an age**.
- Small screen: browser DevTools responsive mode 390 x 844 and 768 x 1024; use horizontal patient selector and scroll tabs. No clipped form inputs or overlay.
- Dark and light theme: inspect Login, patient header, summary cards, clinical tabs, VoiceBridge notes and form inputs.
- Staff: sign in as your existing admin, doctor, nurse, and lab users separately. Confirm allowed actions by role. Never share demo passwords in Git or screenshots.
- VoiceBridge: expansion, note entry, note approval under doctor or nurse, notes list; test reminder as mock only.

## Verification
- TypeScript `npx tsc --noEmit` completed successfully in build environment.
- Python compilation completed successfully.
- Backend tests: 4 passed.
- Vite production build was **not** completed because the build environment lacks the optional Linux Rollup binary (`@rollup/rollup-linux-x64-gnu`). Run `npm ci` on Windows and then `npm run build` in your environment.
- No browser automation or visual regression test completed. Assess at actual screen sizes before committing to live use.

## Current feature status and external dependencies
- **Working demo:** synthetic patient timeline, PDF/image document workflow (OCR dependencies required), deterministic extraction, briefing, draft speech capture (browser-dependent), note review, basic role authentication, patient messaging preferences, queued mock reminders, source catalogue, selected gap checks.
- **Needs external services:** browser dictation uses Web Speech vendor support; server-based multilingual speech/translation not integrated. Accurate scanned-PDF extraction needs Tesseract/Poppler, optionally AWS Textract configuration. Generative summary via Claude needs provider API key and network access; fallback is deterministic.
- **Not implemented:** real WhatsApp/SMS sending (provider credentials, approved templates, consent and delivery worker needed), multilingual translated UI, automated multilingual diarization, claim-level verifiable Evidence Integrity Engine, complete CARE plugin deployment, patient/facility-level fine-grained access controls, fully approved obstetric rulebook, published benchmark metrics, production security/compliance validation.
- **Clinical boundary:** approved patient record statements and documentation availability only; clinical recommendations require review. Synthetic data only.

**Do not upload real patient information or deploy this prototype as a clinical system.**
