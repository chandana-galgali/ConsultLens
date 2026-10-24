"""Rule-based classification + extraction. Deliberately simple and explainable.
Never interprets values (no normal/abnormal) - it only finds what is written."""
import re
from dataclasses import dataclass
from datetime import date

DATE_RE = re.compile(r"\b(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})\b")

# Order matters: first match wins. The first lines of a document (its title) are tested before the whole text,
# so a "Level II scan" report that mentions "nuchal fold" is still a Level II scan.
DOC_RULES = [
    ("marker", r"dual marker|double marker|triple marker|quadruple marker|quad marker|papp-?a|first trimester screening"),
    ("usg_nt", r"nuchal|\bNT scan\b|11\s*(?:-|–|to)\s*13\s*\+?\s*6?\s*w(?:eeks?|ks)"),
    ("usg_level2", r"level\s*(?:ii|2)|anomaly scan|targeted imaging"),
    ("usg_growth", r"growth scan|\bEFW\b|fetal growth"),
    ("usg_doppler", r"doppler"),
    ("usg_other", r"ultrasound|sonograph|\bUSG\b"),
    ("vaccine", r"\bTT\s?[12]\b|tetanus|influenza vaccine|immuni[sz]ation"),
    ("visit", r"anc visit|visit note|follow.?up note|clinic note"),
    ("prescription", r"\brx\b|\btab\.?\s|\bcap\.?\s|\bsyp\b"),
    ("discharge", r"discharge summary"),
    ("lab", r"haemoglobin|hemoglobin|\bhb\b|\bcbc\b|glucose|hba1c|\btsh\b|creatinine"),
    ("serology", r"serology|\bhiv\b|hbsag|vdrl|blood group"),
]

W = 30  # max characters allowed between a test name and its value (names often carry brackets)

# code -> (label, regex with ONE numeric group, unit)
LAB_PATTERNS = {
    # the two lookbehinds keep "Glycosylated Hemoglobin (HbA1c)" from being read as plain hemoglobin
    "hb": ("Hemoglobin", rf"(?<!glycated )(?<!glycosylated )(?:\bhb\b|h[a]?emoglobin)[^0-9\n]{{0,{W}}}(\d{{1,2}}(?:\.\d+)?)", "g/dL"),
    "tlc": ("Total leucocyte count", rf"(?:\btlc\b|total\s*(?:leu[ck]ocyte|wbc)\s*count|\bwbc\b)[^0-9\n]{{0,{W}}}(\d{{1,2}}(?:\.\d+)?)", "x10^3/uL"),
    "platelets": ("Platelets", rf"platelets?(?:\s*count)?[^0-9\n]{{0,{W}}}(\d{{1,3}}(?:[.,]\d+)?)", "x10^3/uL"),
    "fbs": ("Fasting blood sugar", rf"(?:fasting\s*(?:blood\s*|plasma\s*)?(?:sugar|glucose)|\bfbs\b)[^0-9\n]{{0,{W}}}(\d{{2,3}}(?:\.\d+)?)", "mg/dL"),
    "ppbs": ("Post-prandial blood sugar", rf"(?:post\s*-?\s*prandial|\bppbs\b|\bpp\s*(?:sugar|glucose))[^0-9\n]{{0,{W}}}(\d{{2,3}}(?:\.\d+)?)", "mg/dL"),
    "hba1c": ("HbA1c", rf"hba1c[^0-9\n]{{0,{W}}}(\d{{1,2}}(?:\.\d+)?)", "%"),
    "tsh": ("TSH", r"\btsh\b[^0-9\n]{0,40}(\d{1,2}(?:\.\d+)?)", "uIU/mL"),
    "creatinine": ("Serum creatinine", rf"creatinine[^0-9\n]{{0,{W}}}(\d(?:\.\d+)?)", "mg/dL"),
    "sgpt": ("SGPT (ALT)", rf"(?:sgpt|\balt\b|alanine)[^0-9\n]{{0,{W}}}(\d{{1,3}}(?:\.\d+)?)", "U/L"),
    "sgot": ("SGOT (AST)", rf"(?:sgot|\bast\b|aspartate)[^0-9\n]{{0,{W}}}(\d{{1,3}}(?:\.\d+)?)", "U/L"),
    "weight": ("Weight", r"(?:(?<!fetal )weight|\bwt\b)[^0-9\n]{0,10}(\d{2,3}(?:\.\d+)?)", "kg"),
}

# A number followed by weeks/days/times is advice ("TSH every 6 weeks"), not a result.
NUM_END = r"(?!\d)(?!\s*(?:weeks?|wks?|days?|months?|hrs?|hours?|times))"
LAB_PATTERNS = {code: (label, pattern + NUM_END, unit) for code, (label, pattern, unit) in LAB_PATTERNS.items()}

# Scan measurements: only read from ultrasound documents (doc_type starts with "usg")
SCAN_PATTERNS = {
    "nt_mm": ("NT", r"(?:\bNT\b|nuchal\s*translucency)[^0-9\n]{0,25}(\d(?:\.\d+)?)\s*mm", "mm"),
    "crl": ("CRL", r"\bCRL\b[^0-9\n]{0,20}(\d{1,3}(?:\.\d+)?)\s*mm", "mm"),
    "fhr": ("Fetal heart rate", r"(?:\bFHR\b|fetal\s*heart(?:\s*rate)?)[^0-9\n]{0,20}(\d{2,3})", "bpm"),
    "efw": ("Estimated fetal weight", r"\bEFW\b[^0-9\n]{0,25}(\d{3,4})\s*(?:g|gm|gms|grams)\b", "g"),
    "afi": ("AFI", r"\bAFI\b[^0-9\n]{0,20}(\d{1,2}(?:\.\d+)?)", "cm"),
}

RESULT = r"(non[\s\-]?reactive|reactive|negative|positive)"
# code -> (label, regex with ONE text group)
TEXT_PATTERNS = {
    "hiv": ("HIV", rf"\bhiv\b[^\n]{{0,40}}?\b{RESULT}"),
    "hbsag": ("HBsAg", rf"hbsag[^\n]{{0,45}}?\b{RESULT}"),
    "hcv": ("Anti-HCV", rf"(?:anti[\s\-]?hcv|\bhcv\b)[^\n]{{0,40}}?\b{RESULT}"),
    "vdrl": ("VDRL", rf"vdrl[^\n]{{0,40}}?\b{RESULT}"),
}
SCAN_TEXT_PATTERNS = {
    "presentation": ("Presentation", r"presentation[^A-Za-z\n]{0,6}(cephalic|breech|transverse|oblique)"),
    "placenta": ("Placenta", r"placenta[^\n]{0,30}?\b(anterior|posterior|fundal|lateral|low[\s\-]?lying|praevia|previa)"),
}
SCAN_GA_RE = re.compile(r"(?:gestational\s*age|gestation|\bGA\b)[^0-9\n]{0,25}(\d{1,2})\s*w(?:eeks?|ks)?(?:\s*\+?\s*(\d)\s*d(?:ays?)?)?", re.I)
BLOOD_GROUP_RE = re.compile(r"blood\s*group[^:\n]{0,25}:\s*(AB|A|B|O)\b\s*(positive|negative|pos|neg|\+|\-)?", re.I)

BP_RE = re.compile(r"\bBP\b[^0-9\n]{0,10}(\d{2,3})\s*/\s*(\d{2,3})", re.I)
VACCINE_RE = re.compile(r"\b(tdap|TT\s?1|TT\s?2|TT\s?booster|influenza)\b[^\n]*?(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{4})", re.I)
MED_RE = re.compile(r"^\s*(?:\d+\s*[.),:\-]?\s*)?(?:Tab|Cap|Syp|Inj)\b\.?\s+(.+?)\s*$", re.I | re.M)
PLAN_RE = re.compile(r"^\s*(plan|advice|advised|next visit)\s*[:\-]\s*(.+?)\s*$", re.I | re.M)


@dataclass
class Obs:
    code: str
    label: str
    value_num: float | None
    value_text: str | None
    unit: str | None
    observed_on: date | None
    snippet: str


def parse_date(s: str) -> date | None:
    """Day-first (Indian format dd/mm/yyyy)."""
    m = DATE_RE.search(s)
    if not m:
        return None
    d, mth, y = map(int, m.groups())
    try:
        return date(y, mth, d)
    except ValueError:
        return None


def classify(text: str) -> str:
    lines = [ln for ln in text.splitlines() if ln.strip()]
    head = "\n".join(lines[:6])
    for scope in (head, text):
        for doc_type, pattern in DOC_RULES:
            if re.search(pattern, scope, re.I | re.M):
                return doc_type
    return "unknown"


def find_doc_date(text: str) -> date | None:
    # Prefer a date on a line mentioning "date"/"reported"/"collected", else the first date anywhere.
    for line in text.splitlines():
        if re.search(r"date|reported|collected|dated", line, re.I):
            d = parse_date(line)
            if d:
                return d
    return parse_date(text)


def _line_containing(text: str, start: int) -> str:
    s = text.rfind("\n", 0, start) + 1
    e = text.find("\n", start)
    return text[s : e if e != -1 else len(text)].strip()[:300]


def _norm_result(s: str) -> str:
    return re.sub(r"[\s\-]+", "-", s.strip().lower()).capitalize()


def extract_observations(text: str, doc_date: date | None, doc_type: str | None = None) -> list[Obs]:
    out: list[Obs] = []

    def first_number(patterns: dict):
        for code, (label, pattern, unit) in patterns.items():
            for m in re.finditer(pattern, text, re.I):
                try:
                    val = float(m.group(1).replace(",", "."))
                except ValueError:
                    continue
                out.append(Obs(code, label, val, None, unit, doc_date, _line_containing(text, m.start())))
                break  # first match per code per document

    if doc_type != "prescription":  # advice text on a prescription must never become a lab result
        first_number(LAB_PATTERNS)
    is_scan = bool(doc_type and doc_type.startswith("usg"))
    if is_scan:
        first_number(SCAN_PATTERNS)

    for code, (label, pattern) in TEXT_PATTERNS.items():
        m = re.search(pattern, text, re.I)
        if m:
            out.append(Obs(code, label, None, _norm_result(m.group(1)), None, doc_date, _line_containing(text, m.start())))

    m = BLOOD_GROUP_RE.search(text)
    if m:
        rh = {"+": "Positive", "pos": "Positive", "positive": "Positive", "-": "Negative", "neg": "Negative", "negative": "Negative"}.get((m.group(2) or "").lower(), "")
        out.append(Obs("blood_group", "Blood group and Rh", None, f"{m.group(1).upper()} {rh}".strip(), None, doc_date, _line_containing(text, m.start())))

    if is_scan:
        for code, (label, pattern) in SCAN_TEXT_PATTERNS.items():
            m = re.search(pattern, text, re.I)
            if m:
                out.append(Obs(code, label, None, re.sub(r"[\s\-]+", " ", m.group(1)).capitalize(), None, doc_date, _line_containing(text, m.start())))
        m = SCAN_GA_RE.search(text)
        if m:
            ga = f"{m.group(1)}w" + (f" {m.group(2)}d" if m.group(2) else "")
            out.append(Obs("scan_ga", "Gestation by scan", None, ga, None, doc_date, _line_containing(text, m.start())))

    m = BP_RE.search(text)
    if m:
        snip = _line_containing(text, m.start())
        out.append(Obs("bp_sys", "BP systolic", float(m.group(1)), None, "mmHg", doc_date, snip))
        out.append(Obs("bp_dia", "BP diastolic", float(m.group(2)), None, "mmHg", doc_date, snip))

    for m in VACCINE_RE.finditer(text):
        name = re.sub(r"\s", "", m.group(1)).lower()  # tt1, tt2, ttbooster, tdap, influenza
        out.append(Obs(name, "Tdap" if name == "tdap" else name.upper(), None, "recorded", None,
                       parse_date(m.group(2)) or doc_date, _line_containing(text, m.start())))

    for m in MED_RE.finditer(text):
        line = m.group(0).strip()
        shown = re.sub(r"^\d+\s*[.),:\-]?\s*", "", line)  # drop the "1." list number
        out.append(Obs("med", "Medication", None, shown[:190], None, doc_date, line[:300]))

    for m in PLAN_RE.finditer(text):
        line = m.group(0).strip()
        label, body = m.group(1).lower(), m.group(2)
        shown = f"Next visit: {body}" if label.startswith("next") else body
        out.append(Obs("plan", "Plan or advice in note", None, shown[:190], None, doc_date, line[:300]))

    return out
