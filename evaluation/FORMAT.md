# Evaluation protocol

This scorer deliberately has **no pre-populated performance results**. Input data must be synthetic or safely de-identified. Each independently labeled case is a JSON object on one line:

```json
{"patient_id":"SYN-001","gold":["hb|11.2|g/dL|2026-01-01"],"predicted":["hb|11.2|g/dL|2026-01-01"]}
```

Run `python evaluation/score.py evaluation/my_cases.jsonl` from the project root. The scorer outputs TP, FP, FN, precision, recall, and F1 over exact matches. This is **only one metric**; source grounding, abstention, error by scan quality/language, and clinician review time require additional adjudicated evaluation. Split train/test by patient journey, lock the test set, and report CIs on sufficient data.
