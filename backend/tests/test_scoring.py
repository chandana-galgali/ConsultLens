import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'evaluation'))
from score import calculate


def test_metric_denominators_and_values():
    result = calculate([{'gold': ['a', 'b'], 'predicted': ['a', 'c']}])
    assert result['tp'] == 1
    assert result['fp'] == 1
    assert result['fn'] == 1
    assert result['precision'] == result['recall'] == result['f1'] == .5
