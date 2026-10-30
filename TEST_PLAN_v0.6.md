# ConsultLens v0.6 — End-to-End Manual Acceptance Matrix

**Use synthetic data only.** Record date, browser, role, result and a screenshot for each failure.

## A. Access and session — expected results

| ID | Test | Expected |
|---|---|---|
| A01 | Admin logs in using hosted or local credentials | Auth succeeds on correctly configured database |
| A02 | Wrong password, nonexistent email | 401 with generic rejection |
| A03 | Request review API without token | 401 |
| A04 | Lab user opens a patient and evidence review | Read-only checklist, actionable observation review |
| A05 | Lab user posts checklist review manually | 403 |
| A06 | Admin attempts review submission | 403; admin is oversight/read-only for review |
| A07 | Nurse submits checklist reviewed | 201; reviewer/time persist |
| A08 | Doctor corrects observation for another patient ID | 404; cross-patient observation reference rejected |
| A09 | Token expires | Protected endpoints reject; sign in again |

## B. Review workflow

| ID | Test | Expected |
|---|---|---|
| B01 | Select patient with extracted observations | Review list contains source facts and labels |
| B02 | Verify numeric fact, add reason | Review created, observation verified |
| B03 | Correct a numeric fact | Source value preserved in `before`, corrected in `after`, trends refresh |
| B04 | Correct a textual fact | Text correction saved; original value remains in history |
| B05 | Submit a decision without a reason | UI prevents submission; API rejects with 422 |
| B06 | Request clarification | Visible outstanding review with reviewer and time |
| B07 | Mark checklist document unavailable | Review persists; never claims test never performed |
| B08 | Verify unsupported checklist decision via API | 422 |
| B09 | Review same fact twice | Both actions appear in history, latest one is displayed |
| B10 | Refresh page, switch patient, return | All previous decisions persist |
| B11 | Open source for uploaded document | Authenticated source opens; source link matches observation |
| B12 | Delete a document with review history | 409, preserving provenance |
| B13 | PATCH old `/observations/{id}` endpoint | 410; unaudited edits prohibited |

## C. Consultation and inclusivity

| ID | Test | Expected |
|---|---|---|
| C01 | Switch patients from Documents tab | New patient starts on Overview |
| C02 | Reload summary request | Structured summary appears for cases with extractable facts |
| C03 | Light/dark toggle | Contrast preserved; theme remains after reload |
| C04 | Hindi/Marathi/English browser dictation | Draft if browser recognizes speech; unsupported browser shows fallback |
| C05 | Upload synthetic audio without consent | 422, no transcription |
| C06 | Upload synthetic audio with no API key | 503 with clear configuration message |
| C07 | Transcribe with configured provider | Draft generated; staff must review/edit to save |
| C08 | Save approved note as doctor/nurse | Note persists and is listed |
| C09 | Try saving a note as lab user | 403 |
| C10 | Open interface at 1440px, 1024px, 768px and 390px widths | Navigation and review actions readable; no horizontal page overflow or overlapping panels |

## D. Reminders and deployment

| ID | Test | Expected |
|---|---|---|
| D01 | Queue reminder before consent | 409 |
| D02 | Save phone and opt-in, queue future reminder | `queued_mock` only; no real messages sent |
| D03 | Queue reminder for past date | 422 |
| D04 | Render `/health` | 200 with `status: ok` |
| D05 | Vercel Network request login and reviews | Calls HTTPS Render base URL, not `localhost` |
| D06 | Redeploy Render with Postgres and S3 | Accounts, adjudications, and original uploaded files remain available |
| D07 | Temporarily block S3 bucket in a safe test environment | Upload fails with 503, does not misleadingly report success |

## Automated

From `backend/`: `python -m pytest -q` (8 checks at package time). Test schema upgrades against a backup database. From `frontend/`: `npm ci && npm run build`. The production frontend build was not verified in the packaging environment because dependencies were unavailable.

## Hackathon demo scenario

1. Login as admin, show staff management; switch to doctor.
2. Open Priya (synthetic), show longitudinal history and source-linked summary.
3. Open Evidence review, verify a correct Hb value; correct a deliberately incorrect test value with a reason.
4. Show original source and before/after values in review history.
5. Review a missing documentation item as unavailable and explain the distinction between missing in records vs not performed.
6. Open Care workspace, dictate or transcribe a synthetic Hindi/Marathi note and approve it.
7. Show a mock consent-based reminder and switch to lab role for access demonstration.
8. Refresh the app and verify review history remains unchanged.
9. Present benchmark plan and results **only for measurements actually run**. Never claim clinical accuracy from this demo alone.
