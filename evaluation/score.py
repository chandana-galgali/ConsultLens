"""Compute exact-match extraction quality from independently labeled JSONL cases.

Input line schema: {"patient_id":"synthetic-id", "gold":["field|value|unit|date"],
"predicted":["field|value|unit|date"]}. Use one patient per line. No PHI.
"""
import argparse
import json
from pathlib import Path


def calculate(cases: list[dict]) -> dict[str, float | int]:
    tp = fp = fn = 0
    for case in cases:
        gold = set(case['gold'])
        predicted = set(case['predicted'])
        tp += len(gold & predicted)
        fp += len(predicted - gold)
        fn += len(gold - predicted)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {'cases': len(cases), 'tp': tp, 'fp': fp, 'fn': fn,
            'precision': round(precision, 5), 'recall': round(recall, 5), 'f1': round(f1, 5)}


def main() -> None:
    parser = argparse.ArgumentParser(description='Score synthetic ConsultLens extraction predictions')
    parser.add_argument('jsonl', type=Path)
    args = parser.parse_args()
    lines = args.jsonl.read_text(encoding='utf-8').splitlines()
    cases = [json.loads(line) for line in lines if line.strip()]
    print(json.dumps(calculate(cases), indent=2))


if __name__ == '__main__':
    main()
