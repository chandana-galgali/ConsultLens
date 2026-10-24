"""Builds the separate, doctor-facing sections of the briefing from the database.
Everything here is retrieval and arithmetic: no interpretation, no normal/abnormal."""
import json
import re
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

from .. import models
from ..catalog import MATRIX_GROUPS, SCAN_CODES, SCAN_SPECS, SPECIAL_MARKERS, SPECIAL_NOT_EXTRACTED, VACCINES
from .timeline_builder import fmt_ga, ga_weeks, obs_value

IMAGE_EXT, PDF_EXT, TEXT_EXT = {".png", ".jpg", ".jpeg"}, {".pdf"}, {".txt", ".md"}


def parse_profile(p: models.Patient) -> dict:
    raw = p.profile
    if not isinstance(raw, str) or not raw.strip():
        return {}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except ValueError:
        return {}


def preview_kind(filename: str) -> str:
    ext = Path(filename or "").suffix.lower()
    return "image" if ext in IMAGE_EXT else "pdf" if ext in PDF_EXT else "text" if ext in TEXT_EXT else "file"


def _iso(d: date | None) -> str | None:
    return d.isoformat() if isinstance(d, date) else None


def _fmt_obs(o) -> str:
    v = obs_value(o)
    return f"{o.label} {v:g} {o.unit}".strip() if isinstance(v, float) else f"{o.label} {v}"


def trimester(ga_wk: float | None) -> int | None:
    if ga_wk is None:
        return None
    return 1 if ga_wk < 14 else 2 if ga_wk < 28 else 3


def build_snapshot(p, docs, gaps, today: date) -> dict:
    visits = sorted([d for d in docs if d.doc_type == "visit" and d.doc_date], key=lambda d: d.doc_date)
    last_visit = visits[-1].doc_date if visits else None
    new_since = [d for d in docs if last_visit and d.doc_date and d.doc_date > last_visit]
    uploads = [d.uploaded_at for d in docs if isinstance(d.uploaded_at, datetime)]
    return {
        "documents": len(docs),
        "last_upload": max(uploads).isoformat() if uploads else None,
        "visit_count": len(visits),
        "last_visit": _iso(last_visit),
        "days_since_last_visit": (today - last_visit).days if last_visit else None,
        "not_found": sum(1 for i in gaps["items"] if i["status"] == "not_found_window_passed"),
        "window_open": sum(1 for i in gaps["items"] if i["status"] == "due_now"),
        "quality_flags": len(gaps["quality"]),
        "new_since_visit": len(new_since),
        "trimester": trimester(gaps.get("ga_weeks")),
    }


def build_since_last_visit(p, docs, obs_by_doc, snapshot) -> list[dict]:
    if not snapshot["last_visit"]:
        return []
    last = date.fromisoformat(snapshot["last_visit"])
    out = []
    for d in sorted(docs, key=lambda d: (d.doc_date is None, d.doc_date)):
        if d.doc_date and d.doc_date > last:
            vals = [_fmt_obs(o) for o in obs_by_doc.get(d.id, []) if o.code not in ("med", "plan")]
            out.append({"doc_id": d.id, "doc_type": d.doc_type, "date": _iso(d.doc_date), "ga": fmt_ga(p.lmp, d.doc_date),
                        "source": d.source, "filename": d.filename, "values": vals[:6]})
    return out


def build_plan_notes(p, docs, obs_by_doc) -> dict | None:
    """Plan / advice lines copied verbatim from the most recent note that has any."""
    for d in sorted([d for d in docs if d.doc_date], key=lambda d: d.doc_date, reverse=True):
        items = [o.value_text for o in obs_by_doc.get(d.id, []) if o.code == "plan" and o.value_text]
        if items:
            return {"doc_id": d.id, "doc_type": d.doc_type, "date": _iso(d.doc_date), "ga": fmt_ga(p.lmp, d.doc_date), "items": items}
    return None


def build_matrix(p, docs, obs) -> dict:
    """Investigations laid out like the clinic's paper trend table: tests down, dates across."""
    wanted = {code for _, rows in MATRIX_GROUPS for code, _, _ in rows}
    rel = [o for o in obs if o.code in wanted and o.observed_on]
    dates = sorted({o.observed_on for o in rel})
    columns = [{"date": d.isoformat(), "ga": fmt_ga(p.lmp, d)} for d in dates]
    by_code: dict[str, dict] = defaultdict(dict)
    for o in sorted(rel, key=lambda o: o.id or 0):
        by_code[o.code].setdefault(o.observed_on.isoformat(), o)
    groups = []
    for title, rows in MATRIX_GROUPS:
        out_rows = []
        for code, label, unit in rows:
            cells = {
                day: {"value": obs_value(o), "doc_id": o.document_id, "obs_id": o.id, "verified": bool(o.verified), "edited": bool(o.edited)}
                for day, o in by_code.get(code, {}).items()
            }
            out_rows.append({"code": code, "label": label, "unit": unit, "cells": cells})
        groups.append({"title": title, "rows": out_rows})
    return {"columns": columns, "groups": groups}


def build_special(docs) -> list[dict]:
    rows = []
    markers = [d for d in docs if d.doc_type == "marker"]
    for key, label, pat in SPECIAL_MARKERS:
        hit = next((d for d in markers if re.search(pat, (d.ocr_text or ""), re.I)), None)
        rows.append({"key": key, "label": label, "found": bool(hit), "doc_id": hit.id if hit else None, "date": _iso(hit.doc_date) if hit else None})
    for label in SPECIAL_NOT_EXTRACTED:
        rows.append({"key": label, "label": label, "found": False, "doc_id": None, "date": None, "note": "Not read automatically"})
    return rows


def build_vitals(trends) -> list[dict]:
    return [t for t in trends if t["code"] in ("weight", "bp")]


def build_scans(p, docs, obs_by_doc, rules) -> list[dict]:
    windows = {r["id"]: r["window_weeks"] for r in rules["expected"]}
    rows = []
    for key, label, rule_id in SCAN_SPECS:
        window = f"{windows[rule_id][0]:g} to {windows[rule_id][1]:g} wks" if rule_id in windows else None
        found = sorted([d for d in docs if d.doc_type == key], key=lambda d: (d.doc_date is None, d.doc_date))
        if not found:
            if key in ("usg_other", "usg_doppler"):
                continue  # optional rows are only shown when a report exists
            rows.append({"scan": label, "found": False, "window": window, "doc_id": None, "date": None, "ga": None, "findings": []})
            continue
        for d in found:
            findings = [{"label": o.label, "value": obs_value(o), "unit": o.unit}
                        for o in obs_by_doc.get(d.id, []) if o.code in SCAN_CODES]
            rows.append({"scan": label, "found": True, "window": window, "doc_id": d.id, "date": _iso(d.doc_date),
                         "ga": fmt_ga(p.lmp, d.doc_date), "findings": findings, "filename": d.filename, "source": d.source})
    return rows


def build_immunisation(p, obs) -> list[dict]:
    rows = []
    for code, label in VACCINES:
        hit = sorted([o for o in obs if o.code == code and o.observed_on], key=lambda o: o.observed_on)
        if hit:
            o = hit[0]
            rows.append({"code": code, "label": label, "found": True, "date": _iso(o.observed_on), "ga": fmt_ga(p.lmp, o.observed_on), "doc_id": o.document_id})
        elif code != "tdap":
            rows.append({"code": code, "label": label, "found": False, "date": None, "ga": None, "doc_id": None})
    return rows


def _norm_med(line: str) -> str:
    s = re.sub(r"^\s*\d+[.)]\s*", "", line or "")
    return re.sub(r"\s+", " ", s).strip().lower()


def build_medications(p, docs, obs_by_doc) -> dict:
    lists = []
    for d in docs:
        items = [o.value_text for o in obs_by_doc.get(d.id, []) if o.code == "med" and o.value_text]
        if items:
            lists.append({"doc_id": d.id, "date": _iso(d.doc_date), "ga": fmt_ga(p.lmp, d.doc_date), "source": d.source,
                          "filename": d.filename, "items": items})
    lists.sort(key=lambda m: (m["date"] is None, m["date"] or ""), reverse=True)
    dated = [m for m in lists if m["date"]]
    diff = None
    if len(dated) >= 2:
        latest, prev = {_norm_med(i) for i in dated[0]["items"]}, {_norm_med(i) for i in dated[1]["items"]}
        diff = {
            "latest_date": dated[0]["date"], "previous_date": dated[1]["date"],
            "not_in_previous": [i for i in dated[0]["items"] if _norm_med(i) not in prev],
            "not_in_latest": [i for i in dated[1]["items"] if _norm_med(i) not in latest],
        }
    return {"lists": lists, "diff": diff}


def build_documents(p, docs, obs_by_doc, quality) -> list[dict]:
    flags: dict[int, list[str]] = defaultdict(list)
    for q in quality:
        if q.get("doc_id"):
            flags[q["doc_id"]].append(q["type"])
    out = []
    for d in sorted(docs, key=lambda d: (d.doc_date is None, d.doc_date), reverse=True):
        up = d.uploaded_at
        out.append({
            "id": d.id, "filename": d.filename, "doc_type": d.doc_type, "date": _iso(d.doc_date), "ga": fmt_ga(p.lmp, d.doc_date),
            "source": d.source, "preview": preview_kind(d.filename), "ocr_engine": d.ocr_engine,
            "ocr_confidence": d.ocr_confidence if isinstance(d.ocr_confidence, (int, float)) else None,
            "uploaded_at": up.isoformat() if isinstance(up, datetime) else None,
            "values": len([o for o in obs_by_doc.get(d.id, []) if o.code not in ("plan",)]),
            "flags": flags.get(d.id, []),
        })
    return out


def build_ruler(p, docs, gaps) -> dict | None:
    """Data for the gestational-age ruler: where today is, where each document sits, and the expected windows."""
    ga = gaps.get("ga_weeks")
    if ga is None:
        return None
    ticks = []
    for d in docs:
        w = ga_weeks(p.lmp, d.doc_date)
        if w is not None and 0 <= w <= 42:
            ticks.append({"week": w, "doc_id": d.id, "doc_type": d.doc_type, "date": _iso(d.doc_date), "source": d.source})
    ticks.sort(key=lambda t: t["week"])
    windows = [{k: i[k] for k in ("id", "label", "group", "lo", "hi", "status", "found_doc_id", "found_on")} for i in gaps["items"]]
    return {"today_week": min(ga, 42), "ticks": ticks, "windows": windows}
