"""Compares the clinic's expected-items schedule against what exists in the record,
and flags record-quality problems (missing dates, conflicting values, EDD mismatch, low OCR confidence...)."""
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import yaml

from .. import models
from .timeline_builder import fmt_ga

RULES_PATH = Path(__file__).parent.parent / "rules" / "antenatal_schedule.yaml"
LOW_OCR_CONFIDENCE = 75.0


def load_rules() -> dict:
    return yaml.safe_load(RULES_PATH.read_text())


def _find(rule: dict, docs, obs, patient_lmp: date | None = None):
    """Returns (found, doc_id, date) for the first piece of evidence in the record."""
    lo, hi = rule["window_weeks"]
    if rule["kind"] == "document":
        for d in sorted(docs, key=lambda d: (d.doc_date is None, d.doc_date)):
            if d.doc_type in rule["doc_types"] and d.doc_date is not None:
                # Only evidence dated inside the configured gestational window satisfies it.
                if patient_lmp is not None and lo <= (d.doc_date - patient_lmp).days / 7 <= hi:
                    return True, d.id, d.doc_date
        return False, None, None
    for o in sorted(obs, key=lambda o: (o.observed_on is None, o.observed_on)):
        if o.code in rule["codes"] and o.observed_on is not None and patient_lmp is not None:
            if lo <= (o.observed_on - patient_lmp).days / 7 <= hi:
                return True, o.document_id, o.observed_on
    return False, None, None


def _quality_checks(patient: models.Patient, docs, obs, today: date) -> list[dict]:
    q = []
    for d in docs:
        if d.doc_date is None:
            q.append({"type": "no_date", "doc_id": d.id, "message": f"{d.filename}: no readable date. Set the date so it appears in the right place on the timeline."})
        elif d.doc_date > today:
            q.append({"type": "future_date", "doc_id": d.id, "message": f"{d.filename}: dated in the future ({d.doc_date.strftime('%d %b %Y')})."})
        elif patient.lmp and d.doc_date < patient.lmp:
            q.append({"type": "before_lmp", "doc_id": d.id, "message": f"{d.filename}: dated {d.doc_date.strftime('%d %b %Y')}, before the recorded LMP."})
        if d.doc_type == "unknown":
            q.append({"type": "unclassified", "doc_id": d.id, "message": f"{d.filename}: could not classify; choose the document type."})
        conf = d.ocr_confidence
        if isinstance(conf, (int, float)) and conf < LOW_OCR_CONFIDENCE:
            q.append({"type": "low_confidence", "doc_id": d.id,
                      "message": f"{d.filename}: OCR confidence {conf:.0f}%. Check the extracted values against the original."})

    # Same parameter, same day, different values (possible OCR error or two sources disagreeing)
    seen = defaultdict(set)
    for o in obs:
        if o.value_num is not None and o.observed_on:
            seen[(o.code, o.observed_on)].add(o.value_num)
    for (code, day), vals in seen.items():
        if len(vals) > 1:
            q.append({"type": "conflict", "message": f"{code.upper()} has different values on {day.strftime('%d %b %Y')}: {sorted(vals)}. Check the source documents."})

    if patient.lmp:
        calc_edd = patient.lmp + timedelta(days=280)
        if patient.edd and abs((patient.edd - calc_edd).days) > 7:
            q.append({"type": "edd_mismatch",
                      "message": f"Recorded EDD {patient.edd.strftime('%d %b %Y')} differs from the LMP-based EDD {calc_edd.strftime('%d %b %Y')} by more than 7 days."})
    return q


def check_gaps(db, patient: models.Patient, today: date | None = None) -> dict:
    today = today or date.today()
    docs = db.query(models.Document).filter_by(patient_id=patient.id).all()
    obs = db.query(models.Observation).filter_by(patient_id=patient.id).all()

    if not patient.lmp:
        quality = [{"type": "missing_lmp", "message": "LMP not recorded; gestational age and expected-item windows are unavailable."}]
        return {"ga": None, "ga_weeks": None, "items": [], "quality": quality + _quality_checks(patient, docs, obs, today)}

    rules = load_rules()
    ga = (today - patient.lmp).days / 7

    items = []
    for r in rules["expected"]:
        lo, hi = r["window_weeks"]
        found, doc_id, on = _find(r, docs, obs, patient.lmp)
        if found:
            status = "found"
        elif ga < lo:
            status = "upcoming"
        elif ga <= hi:
            status = "due_now"
        else:
            status = "not_found_window_passed"
        items.append({
            "id": r["id"], "label": r["label"], "group": r.get("group") or r["label"], "window": f"{lo:g} to {hi:g} wks", "lo": lo, "hi": hi, "status": status, "review_required": True, "clinical_recommendation": False,
            "found_doc_id": doc_id, "found_on": on.isoformat() if on else None,
        })

    return {
        "ga": fmt_ga(patient.lmp, today),
        "ga_weeks": round(ga, 2),
        "edd_by_lmp": (patient.lmp + timedelta(days=280)).isoformat(),
        "rules_version": rules["version"],
        "rules_note": rules["note"],
        "items": items,
        "quality": _quality_checks(patient, docs, obs, today),
    }
