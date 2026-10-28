from datetime import date
from types import SimpleNamespace

from app.security import check_password, hash_password
from app.services.gap_checker import _find


def test_password_hash_is_salted_and_verifiable():
    a = hash_password('safe-demo-password-123')
    b = hash_password('safe-demo-password-123')
    assert a != b
    assert check_password('safe-demo-password-123', a)
    assert not check_password('wrong', a)


def test_document_requires_correct_gestational_window():
    rule = {'kind': 'document', 'window_weeks': [11, 14], 'doc_types': ['usg_nt']}
    lmp = date(2026, 1, 1)
    early = SimpleNamespace(id=1, doc_type='usg_nt', doc_date=date(2026, 1, 30))
    valid = SimpleNamespace(id=2, doc_type='usg_nt', doc_date=date(2026, 4, 1))
    undated = SimpleNamespace(id=3, doc_type='usg_nt', doc_date=None)
    assert _find(rule, [early, undated], [], lmp)[0] is False
    assert _find(rule, [early, undated, valid], [], lmp)[1] == 2


def test_observation_requires_date_and_window_even_when_old_rule_skips_match():
    rule = {'kind': 'observation', 'window_weeks': [24, 28], 'codes': ['hb']}
    lmp = date(2026, 1, 1)
    old = SimpleNamespace(code='hb', observed_on=date(2026, 2, 1), document_id=1)
    unknown = SimpleNamespace(code='hb', observed_on=None, document_id=2)
    assert _find(rule, [], [old, unknown], lmp)[0] is False
