"""
demo_data.py — Synthetic antenatal patients for ConsultLens demo.

ALL data is SYNTHETIC and invented for demonstration purposes only.
No real patient records are used. Do not use this data clinically.
"""

from datetime import date, timedelta
from typing import List, Dict, Any

# ── Patient definitions ───────────────────────────────────────────────────────
# We define 3 patients with different gestational ages and risk profiles.

def today() -> date:
    return date.today()


DEMO_PATIENTS: List[Dict[str, Any]] = [
    # ── Patient 1: Priya Sharma — 26+2 wks, rising BP, missing Level II scan ──
    {
        "name": "Priya Sharma",
        "age_years": 27,
        "lmp": str(today() - timedelta(weeks=26, days=2)),
        "whatsapp_number": "+91-9876543210",
        "documents": [
            {
                "original_filename": "ANC_Booking_Visit_Priya.txt",
                "doc_type": "visit",
                "doc_date": str(today() - timedelta(weeks=24)),
                "text": """
ANTENATAL BOOKING VISIT
Patient: Priya Sharma | Age: 27 years | Date: {d1}
LMP: {lmp} | EDD: {edd} | GA: 8+3 weeks

VITALS:
BP: 110/72 mmHg
Weight: 54.2 kg
Height: 158 cm
Pulse: 78/min
Temperature: 98.6°F

INVESTIGATIONS ORDERED:
Hb, Blood group and Rh typing, VDRL, HIV, HBsAg, HCV, FBS, TSH, Urine R/M
""".format(
                    d1=str(today() - timedelta(weeks=24)),
                    lmp=str(today() - timedelta(weeks=26, days=2)),
                    edd=str(today() + timedelta(weeks=13, days=5)),
                ),
            },
            {
                "original_filename": "Lab_Report_8wks_Priya.txt",
                "doc_type": "lab",
                "doc_date": str(today() - timedelta(weeks=23, days=5)),
                "text": """
CLINICAL PATHOLOGY REPORT
Patient: Priya Sharma  Date: {d}
Ref by: Dr. Anita Mehta

HAEMATOLOGY:
Haemoglobin (Hb): 10.8 g/dL
TLC: 8400 cells/cumm
Platelets: 2.1 lakh/cumm

BLOOD GROUPING:
Blood Group: B Positive (B+)

SEROLOGY:
HIV I & II: Non-Reactive
HBsAg (Hepatitis B Surface Antigen): Non-Reactive
HCV Antibody: Non-Reactive
VDRL: Non-Reactive

BIOCHEMISTRY:
FBS (Fasting Blood Sugar): 84 mg/dL
TSH: 2.1 mIU/L
Serum Creatinine: 0.7 mg/dL
SGPT (ALT): 22 IU/L
SGOT (AST): 19 IU/L
""".format(d=str(today() - timedelta(weeks=23, days=5))),
            },
            {
                "original_filename": "NT_Scan_11wks_Priya.txt",
                "doc_type": "usg_nt",
                "doc_date": str(today() - timedelta(weeks=19, days=3)),
                "text": """
ULTRASONOGRAPHY REPORT — NT SCAN
Patient: Priya Sharma  Date: {d}
GA by LMP: 11+2 weeks

FINDINGS:
CRL: 48 mm
Nuchal Translucency (NT): 1.6 mm (within normal limits for this gestational age)
FHR: 164 bpm (regular)
Nasal bone: Present
Crown Rump Length corresponds to 11+4 weeks by scan

IMPRESSION:
Single live intrauterine gestation of 11+4 weeks. NT within reference range.
No structural abnormalities detected at this gestation.
""".format(d=str(today() - timedelta(weeks=19, days=3))),
            },
            {
                "original_filename": "TT_Vaccine_Record_Priya.txt",
                "doc_type": "vaccine",
                "doc_date": str(today() - timedelta(weeks=18)),
                "text": """
IMMUNISATION RECORD
Patient: Priya Sharma  Date: {d}
GA: 12+2 weeks

Tetanus Toxoid (TT1) — 0.5 mL IM given in left arm
Next dose: TT2 to be given 4 weeks later
""".format(d=str(today() - timedelta(weeks=18))),
            },
            {
                "original_filename": "ANC_Visit_18wks_Priya.txt",
                "doc_type": "visit",
                "doc_date": str(today() - timedelta(weeks=11)),
                "text": """
ANTENATAL FOLLOW-UP VISIT
Patient: Priya Sharma  Date: {d}
GA: 18+5 weeks

VITALS:
BP: 116/74 mmHg
Weight: 56.8 kg  (weight gain +2.6 kg since booking)
FHR: 148 bpm (via Doppler)
Fundal height: 19 cm

URINE: Albumin — Nil, Sugar — Nil

Plan: Level II scan to be arranged at 18–20 weeks
Patient counselled on foetal movements, diet, iron supplements
""".format(d=str(today() - timedelta(weeks=11))),
            },
            {
                "original_filename": "Lab_PPBS_20wks_Priya.txt",
                "doc_type": "lab",
                "doc_date": str(today() - timedelta(weeks=9)),
                "text": """
BIOCHEMISTRY REPORT
Patient: Priya Sharma  Date: {d}
GA at collection: 20+1 weeks

Post Prandial Blood Sugar (PPBS) (2-hour): 134 mg/dL
HbA1c: 5.4%
Haemoglobin (Hb): 10.2 g/dL
TLC: 7900 cells/cumm
Platelets: 2.05 lakh/cumm
""".format(d=str(today() - timedelta(weeks=9))),
            },
            {
                "original_filename": "ANC_Visit_24wks_Priya.txt",
                "doc_type": "visit",
                "doc_date": str(today() - timedelta(weeks=4)),
                "text": """
ANTENATAL FOLLOW-UP VISIT
Patient: Priya Sharma  Date: {d}
GA: 24+2 weeks

VITALS:
BP: 128/82 mmHg  ← slightly elevated, repeat in 2 weeks
Weight: 59.4 kg  (weight gain +5.2 kg from booking)
Fundal height: 24 cm
FHR: 152 bpm (regular)

URINE: Albumin — trace (+1), Sugar — Nil

Foetal movements reported by patient: Yes, active

Plan:
- Repeat BP at next visit
- Repeat Hb
- Organise Level II morphology scan (overdue — was planned at 18–20 weeks)
- Urine culture sent
""".format(d=str(today() - timedelta(weeks=4))),
            },
        ],
    },

    # ── Patient 2: Sunita Devi — 36+4 wks, high risk, on Labetalol, Hb 8.4 ──
    {
        "name": "Sunita Devi",
        "age_years": 32,
        "lmp": str(today() - timedelta(weeks=36, days=4)),
        "whatsapp_number": "+91-9823456789",
        "documents": [
            {
                "original_filename": "ANC_Booking_Sunita.txt",
                "doc_type": "visit",
                "doc_date": str(today() - timedelta(weeks=32)),
                "text": """
ANTENATAL BOOKING — REFERRED CASE
Patient: Sunita Devi | Age: 32 years | Date: {d}
G3 P2 L2 | LMP: {lmp} | EDD: {edd}  GA at booking: 10+2 weeks
Referred from PHC Nandurbar

Known hypertension — on Tab Methyldopa 250 mg BD since 2 months
H/O gestational hypertension in previous pregnancy (2019)
Previous deliveries: LSCS x2

VITALS AT BOOKING:
BP: 136/90 mmHg
Weight: 67.4 kg
Pulse: 82/min

PLAN: High-risk pregnancy. Frequent monitoring. Maternal medicine referral.
""".format(
                    d=str(today() - timedelta(weeks=32)),
                    lmp=str(today() - timedelta(weeks=36, days=4)),
                    edd=str(today() + timedelta(weeks=3, days=3)),
                ),
            },
            {
                "original_filename": "Labs_Booking_Sunita.txt",
                "doc_type": "lab",
                "doc_date": str(today() - timedelta(weeks=31)),
                "text": """
PATHOLOGY REPORT — BOOKING INVESTIGATIONS
Patient: Sunita Devi  Date: {d}

Haemoglobin (Hb): 9.2 g/dL
Blood Group: A Positive (A+)
TLC: 9600 cells/cumm
Platelets: 1.98 lakh/cumm
MCV: 71 fL

FBS: 91 mg/dL
PPBS: 128 mg/dL
HbA1c: 5.6%
TSH: 3.1 mIU/L
Serum Creatinine: 0.8 mg/dL
SGPT (ALT): 18 IU/L
SGOT (AST): 21 IU/L

HIV: Non-Reactive
HBsAg: Non-Reactive
HCV: Non-Reactive
VDRL: Non-Reactive
""".format(d=str(today() - timedelta(weeks=31))),
            },
            {
                "original_filename": "NT_Scan_12wks_Sunita.txt",
                "doc_type": "usg_nt",
                "doc_date": str(today() - timedelta(weeks=29)),
                "text": """
ULTRASONOGRAPHY — DATING & NT SCAN
Patient: Sunita Devi  Date: {d}
GA by LMP: 12+0 weeks

CRL: 55 mm
NT: 1.8 mm
FHR: 158 bpm (regular, regular)
Nasal Bone: Present
Placenta: Posterior, high
No subchorionic haematoma

IMPRESSION: Single live intrauterine pregnancy of 12+1 weeks by biometry.
NT within reference limits.
""".format(d=str(today() - timedelta(weeks=29))),
            },
            {
                "original_filename": "Level2_Scan_20wks_Sunita.txt",
                "doc_type": "usg_level2",
                "doc_date": str(today() - timedelta(weeks=21)),
                "text": """
ANOMALY SCAN — LEVEL II USG
Patient: Sunita Devi  Date: {d}
GA by LMP: 20+0 weeks

Fetal Biometry:
  BPD: 47 mm
  HC: 180 mm
  AC: 162 mm
  FL: 34 mm
  EFW: 320 grams (10th–50th centile)

AFI (Amniotic Fluid Index): 14 cm (normal range)
FHR: 144 bpm
Presentation: Cephalic
Placenta: Posterior, not low lying, Grade 0
Umbilical artery Doppler: Normal flow, no notching

No gross structural anomaly detected.

IMPRESSION: Single live intrauterine pregnancy, 20+2 weeks by biometry.
EFW appropriate for gestational age. No anomaly detected. Placenta posterior, high.
""".format(d=str(today() - timedelta(weeks=21))),
            },
            {
                "original_filename": "TT_Record_Sunita.txt",
                "doc_type": "vaccine",
                "doc_date": str(today() - timedelta(weeks=26)),
                "text": """
IMMUNISATION RECORD — Sunita Devi
Date: {d}  GA: 16+0 weeks

TT1 — 0.5 mL IM given. (Previously immunised status verified from MCP card)
TT2 — 0.5 mL IM given (4 weeks later — {d2})
""".format(
                    d=str(today() - timedelta(weeks=26)),
                    d2=str(today() - timedelta(weeks=22)),
                ),
            },
            {
                "original_filename": "Prescription_28wks_Sunita.txt",
                "doc_type": "prescription",
                "doc_date": str(today() - timedelta(weeks=14)),
                "text": """
PRESCRIPTION
Patient: Sunita Devi  Date: {d}  GA: 28+0 weeks

BP at visit: 148/94 mmHg — Antihypertensive dose adjusted.

Tab Labetalol 100 mg — TDS (three times daily)
Tab Methyldopa 250 mg — BD (twice daily) — continue
Tab Ferrous sulphate + Folic acid — OD
Inj Dexamethasone 6 mg IM — given (for foetal lung maturity, repeat in 24 hours)
Cal + Vit D — OD

Review in 1 week. BP monitoring at home daily, record in diary.
Urine protein dipstick daily.
""".format(d=str(today() - timedelta(weeks=14))),
            },
            {
                "original_filename": "Growth_Scan_32wks_Sunita.txt",
                "doc_type": "usg_growth",
                "doc_date": str(today() - timedelta(weeks=10)),
                "text": """
GROWTH SCAN — 32 WEEKS
Patient: Sunita Devi  Date: {d}  GA by LMP: 32+0 weeks

Fetal Biometry:
  BPD: 80 mm
  HC: 295 mm
  AC: 279 mm
  FL: 62 mm
  EFW: 1820 grams (25th–50th centile for GA)

AFI: 12 cm (normal)
Presentation: Cephalic
Placenta: Posterior, not low lying, Grade 2
Umbilical artery Doppler: S/D ratio 3.1, normal end-diastolic flow
MCA Doppler: Normal

IMPRESSION: EFW appropriate for gestation. Doppler parameters normal.
Recommend growth scan at 36 weeks.
""".format(d=str(today() - timedelta(weeks=10))),
            },
            {
                "original_filename": "Labs_32wks_Sunita.txt",
                "doc_type": "lab",
                "doc_date": str(today() - timedelta(weeks=9, days=2)),
                "text": """
REPEAT BLOOD INVESTIGATION
Patient: Sunita Devi  Date: {d}  GA: 32+3 weeks

Haemoglobin (Hb): 8.4 g/dL  (fall from 9.2 — iron supplementation to be reviewed)
TLC: 10200 cells/cumm
Platelets: 1.74 lakh/cumm  (within acceptable range)
Serum Ferritin: 7 ng/mL (low)
Peripheral smear: Hypochromic microcytic anaemia

SGPT (ALT): 24 IU/L
SGOT (AST): 27 IU/L
Serum Creatinine: 0.9 mg/dL
Urine protein: 2+ (24-hr urine protein sent)
""".format(d=str(today() - timedelta(weeks=9, days=2))),
            },
            {
                "original_filename": "ANC_Visit_36wks_Sunita.txt",
                "doc_type": "visit",
                "doc_date": str(today() - timedelta(days=5)),
                "text": """
ANTENATAL VISIT — 36 WEEKS
Patient: Sunita Devi  Date: {d}  GA: 36+2 weeks

VITALS:
BP: 152/96 mmHg  ← persistent elevation — discuss early delivery plan
Weight: 72.8 kg  (total weight gain +5.4 kg)
Fundal height: 35 cm
Presentation: Cephalic, 3/5 engaged
FHR: 138 bpm

URINE: Protein +2, Sugar Nil

PLAN:
- Admit if BP ≥ 160/100 or any symptoms (headache, visual disturbance, epigastric pain)
- Growth scan and Doppler arranged for today
- Discuss delivery plan — aim for 37 weeks
- Neonatologist informed
""".format(d=str(today() - timedelta(days=5))),
            },
        ],
    },

    # ── Patient 3: Meena Krishnan — 9+0 wks, O-negative, first trimester booking ──
    {
        "name": "Meena Krishnan",
        "age_years": 24,
        "lmp": str(today() - timedelta(weeks=9)),
        "whatsapp_number": "+91-9456123780",
        "documents": [
            {
                "original_filename": "Booking_USG_Meena.txt",
                "doc_type": "usg_nt",
                "doc_date": str(today() - timedelta(days=3)),
                "text": """
EARLY PREGNANCY SCAN
Patient: Meena Krishnan | Age: 24 years | Date: {d}
G1 P0 L0 | LMP: {lmp}

FINDINGS:
Single live intrauterine gestational sac
CRL: 22 mm — corresponds to 9+0 weeks
FHR: 172 bpm (regular, reassuring)
Uterus: Anteverted, normal
Ovaries: Normal bilaterally
No subchorionic bleed

IMPRESSION: Single live intrauterine pregnancy, 9+0 weeks. Reassuring cardiac activity.
NT scan and Dual Marker test recommended at 11–13+6 weeks.
""".format(
                    d=str(today() - timedelta(days=3)),
                    lmp=str(today() - timedelta(weeks=9)),
                ),
            },
            {
                "original_filename": "Labs_Booking_Meena.txt",
                "doc_type": "lab",
                "doc_date": str(today() - timedelta(days=2)),
                "text": """
BOOKING BLOOD INVESTIGATIONS
Patient: Meena Krishnan  Date: {d}

Haemoglobin (Hb): 11.4 g/dL
Blood Group: O Negative (O–)  ← Rh negative — IMPORTANT: Anti-D prophylaxis required
TLC: 7200 cells/cumm
Platelets: 2.3 lakh/cumm
MCV: 78 fL (borderline low — investigate for thalassaemia)

FBS: 79 mg/dL
TSH: 1.8 mIU/L
Serum Creatinine: 0.6 mg/dL

HIV I & II: Non-Reactive
HBsAg: Non-Reactive
HCV: Non-Reactive
VDRL: Non-Reactive

Indirect Coombs Test (ICT): Negative

IMPORTANT NOTE: Patient is Rh negative. Husband's blood group required.
Anti-D immunoglobulin 300 mcg to be arranged at 28 weeks.
Repeat ICT at each antenatal visit.
""".format(d=str(today() - timedelta(days=2))),
            },
        ],
    },
]


def get_demo_patients() -> List[Dict[str, Any]]:
    """Return the demo patients list. Each item has name, lmp, documents, etc."""
    return DEMO_PATIENTS


def create_demo_patients(db) -> list:
    """
    Create synthetic demo patients in the database.
    Idempotent: skips patients whose name already exists.
    Returns the list of newly created Patient objects.
    """
    import os
    import tempfile
    from .. import models
    from .pipeline import process_document

    created = []

    for pt_data in DEMO_PATIENTS:
        # Skip if patient already exists
        existing = db.query(models.Patient).filter_by(name=pt_data["name"]).first()
        if existing:
            continue

        from datetime import date as _date
        lmp_val = _date.fromisoformat(pt_data["lmp"]) if pt_data.get("lmp") else None

        pt = models.Patient(
            name=pt_data["name"],
            age=pt_data.get("age_years"),
            phone=pt_data.get("whatsapp_number"),
            lmp=lmp_val,
        )
        db.add(pt)
        db.flush()  # get pt.id

        for doc_data in pt_data.get("documents", []):
            text = doc_data["text"].strip()
            # Write to a temp file so stored_path is valid
            suffix = ".txt"
            fd, tmp_path = tempfile.mkstemp(suffix=suffix, prefix="consultlens_demo_")
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as fh:
                    fh.write(text)
            except Exception:
                os.close(fd)

            doc = models.Document(
                patient_id=pt.id,
                filename=doc_data["original_filename"],
                stored_path=tmp_path,
                source="demo",
                doc_type=doc_data.get("doc_type", "visit"),
            )
            db.add(doc)
            db.flush()

            from datetime import date as _date2
            doc_date = _date2.fromisoformat(doc_data["doc_date"]) if doc_data.get("doc_date") else None
            process_document(db, doc, user_date=doc_date, text_override=text)
            # Preserve original synthetic source when remote storage is configured.
            from .storage import store_processed_file
            from ..config import settings
            if settings.s3_bucket:
                doc.stored_path = store_processed_file(tmp_path)
                os.unlink(tmp_path)

        db.commit()
        db.refresh(pt)
        created.append(pt)

    return created
