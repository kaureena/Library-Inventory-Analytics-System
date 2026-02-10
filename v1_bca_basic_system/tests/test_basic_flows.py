from datetime import date
from v1_bca_basic_system.src.app.rules import due_after_issue, fine_amount


def test_due_after_issue():
    assert due_after_issue(date(2026, 1, 1), date(2026, 1, 2))
    assert not due_after_issue(date(2026, 1, 1), date(2026, 1, 1))


def test_fine_amount():
    assert fine_amount(date(2026, 1, 10), date(2026, 1, 10)) == 0.0
    assert fine_amount(date(2026, 1, 10), date(2026, 1, 12), fine_per_day=1.5) == 3.0
