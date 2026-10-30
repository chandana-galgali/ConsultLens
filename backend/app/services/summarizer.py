"""Narrative summary. Claude is used ONLY to reword structured data we already computed.
Three safety layers: (1) it never sees raw files, only our JSON; (2) the system prompt forbids interpretation;
(3) we scan the output for interpretive words and fall back to a deterministic template if any appear."""
import json
import re

from ..config import settings

SYSTEM = (
    "You format a pre-consultation briefing for an obstetrician from STRUCTURED DATA. "
    "Rules: restate only what is in the data. Do NOT interpret values, do NOT say normal/abnormal/high/low/elevated, "
    "do NOT suggest diagnoses, tests or treatment, do NOT use the words 'should' or 'recommend'. "
    "Mention dates and gestational ages. List items with status not_found_window_passed or due_now "
    "as 'not found in uploaded records'. Max 120 words, plain sentences."
)

BANNED = re.compile(
    r"\b(abnormal|normal|elevated|high|low|concerning|worrying|risk|diagnos\w*|suggest\w*|recommend\w*|should|"
    r"preeclampsia|anemi\w*|anaemi\w*|diabet\w*|hypertens\w*|urgent)\b",
    re.I,
)


def _fmt(pt: dict) -> str:
    if pt.get("display"):
        return str(pt["display"])
    value = pt.get("value")
    return f"{value:g}" if isinstance(value, (float, int)) else str(value or "unavailable")


def _fallback(b: dict) -> str:
    p, snap = b["patient"], b.get("snapshot", {})
    parts = [f"{p['name']}: gestational age {b['gaps'].get('ga') or 'unavailable'}; {len(b.get('events', []))} dated record events available."]
    if snap.get("last_visit"):
        parts.append(f"Last visit note is dated {snap['last_visit']}.")
    for t in b.get("trends", [])[:6]:
        latest = t.get("latest")
        if not latest:
            continue
        previous = t.get("previous") or t.get("prev")
        unit = f" {t['unit']}" if t.get("unit") else ""
        if previous:
            parts.append(f"{t['label']}: {_fmt(previous)} ({previous.get('date', 'undated')}) then {_fmt(latest)}{unit} ({latest.get('date', 'undated')}).")
        else:
            parts.append(f"{t['label']}: {_fmt(latest)}{unit} ({latest.get('date', 'undated')}), one recorded observation.")
    pending = [i["label"] for i in b["gaps"]["items"] if i["status"] in ("due_now", "not_found_window_passed")]
    if pending:
        parts.append("Not found in uploaded records: " + "; ".join(pending) + ".")
    return " ".join(parts)


def summarize(briefing: dict) -> dict:
    if not settings.anthropic_api_key:
        return {"text": _fallback(briefing), "engine": "template"}
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        slim = {
            "patient": {"name": briefing["patient"]["name"]},
            "trends": [{k: t[k] for k in ("label", "unit", "latest", "previous", "delta_display")} for t in briefing["trends"]],
            "gaps": {"ga": briefing["gaps"].get("ga"), "items": [{k: i[k] for k in ("label", "status", "window")} for i in briefing["gaps"]["items"]]},
        }
        msg = client.messages.create(
            model=settings.claude_model, max_tokens=400, system=SYSTEM,
            messages=[{"role": "user", "content": json.dumps(slim, default=str)}],
        )
        text = msg.content[0].text.strip()
        if BANNED.search(text):  # interpretive language slipped in -> do not show it
            return {"text": _fallback(briefing), "engine": "template (guard)"}
        return {"text": text, "engine": settings.claude_model}
    except Exception:
        return {"text": _fallback(briefing), "engine": "template"}
