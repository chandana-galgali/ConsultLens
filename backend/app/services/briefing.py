"""Assembles the full briefing JSON that the doctor workspace renders."""
from collections import defaultdict
from datetime import date

from .. import models
from . import gap_checker, sections, summarizer, timeline_builder


def patient_out(p: models.Patient) -> dict:
    return {
        "id": p.id, "name": p.name, "age": p.age, "mrn": p.mrn, "external_id": p.external_id, "phone": p.phone,
        "blood_group": p.blood_group, "lmp": p.lmp, "edd": p.edd, "gravida": p.gravida, "para": p.para,
        "profile": sections.parse_profile(p),
    }


def patient_card(db, p: models.Patient, today: date | None = None) -> dict:
    """Small summary for the patient list in the sidebar."""
    gaps = gap_checker.check_gaps(db, p, today)
    docs = db.query(models.Document).filter_by(patient_id=p.id).all()
    return {
        **patient_out(p),
        "ga": gaps.get("ga"),
        "documents": len(docs),
        "not_found": sum(1 for i in gaps["items"] if i["status"] == "not_found_window_passed"),
        "window_open": sum(1 for i in gaps["items"] if i["status"] == "due_now"),
        "quality_flags": len(gaps["quality"]),
    }


def build_briefing(db, p: models.Patient, narrative: bool = False, today: date | None = None) -> dict:
    today = today or date.today()
    docs = db.query(models.Document).filter_by(patient_id=p.id).all()
    obs = db.query(models.Observation).filter_by(patient_id=p.id).all()
    obs_by_doc = defaultdict(list)
    for o in obs:
        obs_by_doc[o.document_id].append(o)

    events = timeline_builder.build_events(db, p)
    trends = timeline_builder.build_trends(db, p)
    gaps = gap_checker.check_gaps(db, p, today)
    rules = gap_checker.load_rules()
    snapshot = sections.build_snapshot(p, docs, gaps, today)

    result = {
        "patient": patient_out(p),
        "snapshot": snapshot,
        "ruler": sections.build_ruler(p, docs, gaps),
        "gaps": gaps,
        "trends": trends,
        "since_last_visit": sections.build_since_last_visit(p, docs, obs_by_doc, snapshot),
        "plan_notes": sections.build_plan_notes(p, docs, obs_by_doc),
        "matrix": sections.build_matrix(p, docs, obs),
        "special": sections.build_special(docs),
        "vitals": sections.build_vitals(trends),
        "scans": sections.build_scans(p, docs, obs_by_doc, rules),
        "immunisation": sections.build_immunisation(p, obs),
        "medications": sections.build_medications(p, docs, obs_by_doc),
        "documents": sections.build_documents(p, docs, obs_by_doc, gaps["quality"]),
        "events": events,
        "disclaimer": "Retrieved and organised data only. Not a diagnosis or treatment recommendation. The clinician interprets and decides.",
    }
    if narrative:
        result["narrative"] = summarizer.summarize(result)
    return result
