"""Display catalogue: how extracted codes are grouped and named. Mirrors the clinic's paper antenatal record
(section 4 'Investigations', 6 'USG details', 7 'Clinically important findings', 8 'Immunisation history')."""

DOC_TYPE_LABELS = {
    "lab": "Lab report",
    "serology": "Serology and blood group",
    "marker": "Screening marker report",
    "usg_nt": "NT scan",
    "usg_level2": "Level II scan",
    "usg_growth": "Growth scan",
    "usg_doppler": "Doppler",
    "usg_other": "Ultrasound",
    "vaccine": "Immunisation record",
    "visit": "Visit note",
    "prescription": "Prescription",
    "discharge": "Discharge summary",
    "unknown": "Unclassified document",
}

# Codes shown in the previous-vs-latest table (order follows the paper record's trend table).
TREND_CODES = ["weight", "bp", "fbs", "ppbs", "hb", "tlc", "platelets", "hba1c", "tsh", "creatinine", "sgpt", "sgot", "efw", "afi"]

# Investigations matrix: (group title, [(code, label, unit)])
MATRIX_GROUPS = [
    ("Complete blood count", [("hb", "Hemoglobin", "g/dL"), ("tlc", "Total leucocyte count", "x10^3/uL"), ("platelets", "Platelets", "x10^3/uL")]),
    ("Blood sugar", [("fbs", "Fasting blood sugar", "mg/dL"), ("ppbs", "Post-prandial blood sugar", "mg/dL"), ("hba1c", "HbA1c", "%")]),
    ("Thyroid, kidney and liver", [("tsh", "TSH", "uIU/mL"), ("creatinine", "Serum creatinine", "mg/dL"), ("sgpt", "SGPT (ALT)", "U/L"), ("sgot", "SGOT (AST)", "U/L")]),
    ("Infection screen", [("hiv", "HIV", None), ("hbsag", "HBsAg", None), ("hcv", "Anti-HCV", None), ("vdrl", "VDRL", None)]),
    ("Blood group", [("blood_group", "Blood group and Rh", None)]),
]
MATRIX_CODES = [c for _, rows in MATRIX_GROUPS for c, _, _ in rows]

# USG details (paper record section 6): (key = doc_type, label, rule id for the expected window)
SCAN_SPECS = [
    ("usg_other", "Early or dating scan", None),
    ("usg_nt", "NT scan", "nt_scan"),
    ("usg_level2", "Level II scan", "level2_scan"),
    ("usg_growth", "Growth scan", "growth_scan_1"),
    ("usg_doppler", "Doppler", None),
]
SCAN_CODES = ["scan_ga", "crl", "nt_mm", "fhr", "efw", "afi", "presentation", "placenta"]

# Immunisation history (paper record section 8)
VACCINES = [("tt1", "TT1"), ("tt2", "TT2"), ("tdap", "Tdap"), ("influenza", "Influenza vaccine")]

# Special investigations (paper record section 5)
SPECIAL_MARKERS = [("dual", "Dual marker", r"dual|double"), ("triple", "Triple marker", r"triple"), ("quad", "Quadruple marker", r"quad")]
SPECIAL_NOT_EXTRACTED = ["Husband's blood group", "TORCH titres", "HPLC / hemoglobinopathy screen"]
