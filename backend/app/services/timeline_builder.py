from collections import defaultdict
from datetime import date

from .. import models
from ..catalog import TREND_CODES


def ga_days(lmp: date | None, on: date | None) -> int | None:
    if not lmp or not on:
        return None
    return (on - lmp).days


def ga_weeks(lmp: date | None, on: date | None) -> float | None:
    d = ga_days(lmp, on)
    return None if d is None else round(d / 7, 2)


def fmt_ga(lmp: date | None, on: date | None) -> str | None:
    d = ga_days(lmp, on)
    return None if d is None or d < 0 else f"{d // 7}+{d % 7}"


def obs_value(o):
    return o.value_num if o.value_num is not None else o.value_text


def build_events(db, patient: models.Patient) -> list[dict]:
    docs = db.query(models.Document).filter_by(patient_id=patient.id).all()
    obs = db.query(models.Observation).filter_by(patient_id=patient.id).all()
    by_doc: dict[int, list] = defaultdict(list)
    for o in obs:
        by_doc[o.document_id].append(o)

    events = []
    for d in docs:
        events.append({
            "date": d.doc_date.isoformat() if d.doc_date else None,
            "ga": fmt_ga(patient.lmp, d.doc_date),
            "doc_id": d.id,
            "doc_type": d.doc_type,
            "filename": d.filename,
            "source": d.source,
            "observations": [
                {"id": o.id, "code": o.code, "label": o.label, "value": obs_value(o), "unit": o.unit,
                 "snippet": o.snippet, "verified": bool(o.verified), "edited": bool(o.edited)}
                for o in by_doc[d.id]
                if o.code not in ("plan",)  # plan lines are shown in their own panel
            ],
        })
    events.sort(key=lambda e: (e["date"] is None, e["date"] or ""))
    return events


def _fmt_num(x: float) -> str:
    return f"{x:+g}"


def build_trends(db, patient: models.Patient) -> list[dict]:
    """Previous vs latest for every monitored parameter. 'delta' is plain subtraction, never a judgement."""
    obs = db.query(models.Observation).filter(
        models.Observation.patient_id == patient.id,
        models.Observation.value_num.isnot(None),
        models.Observation.observed_on.isnot(None),
    ).all()
    series: dict[str, list] = defaultdict(list)
    for o in obs:
        series[o.code].append(o)

    def pt(o, **extra):
        return {"date": o.observed_on.isoformat(), "value": o.value_num, "doc_id": o.document_id, "obs_id": o.id,
                "ga": fmt_ga(patient.lmp, o.observed_on), "ga_weeks": ga_weeks(patient.lmp, o.observed_on), **extra}

    out = []
    for c in TREND_CODES:
        if c == "bp":
            sys_pts = sorted(series.get("bp_sys", []), key=lambda o: o.observed_on)
            dia_by = {(o.observed_on, o.document_id): o for o in series.get("bp_dia", [])}
            hist = []
            for s in sys_pts:
                dia = dia_by.get((s.observed_on, s.document_id))
                if dia:
                    hist.append(pt(s, dia=dia.value_num, display=f"{s.value_num:g}/{dia.value_num:g}"))
            if not hist:
                continue
            latest, prev = hist[-1], (hist[-2] if len(hist) > 1 else None)
            out.append({
                "code": "bp", "label": "Blood pressure", "unit": "mmHg", "latest": latest, "previous": prev,
                "delta": None,
                "delta_display": f"{_fmt_num(latest['value'] - prev['value'])} / {_fmt_num(latest['dia'] - prev['dia'])}" if prev else None,
                "history": hist,
            })
            continue
        pts = sorted(series.get(c, []), key=lambda o: o.observed_on)
        if not pts:
            continue
        latest, prev = pts[-1], (pts[-2] if len(pts) > 1 else None)
        out.append({
            "code": c, "label": latest.label, "unit": latest.unit,
            "latest": pt(latest), "previous": pt(prev) if prev else None,
            "delta": round(latest.value_num - prev.value_num, 2) if prev else None,
            "delta_display": _fmt_num(round(latest.value_num - prev.value_num, 2)) if prev else None,
            "history": [pt(o) for o in pts],
        })
    return out
