import pytest
from pathlib import Path
import json


def test_dq_summary_present_and_parseable():
    base = Path(__file__).resolve().parents[2]
    p = base / "v2_analytics_modernisation/reports/dq_summary.json"
    if not p.exists():
        pytest.skip("dq_summary.json not present (DQ not run).")
    data = json.loads(p.read_text(encoding="utf-8"))
    assert "overall_status" in data
    assert "rules" in data
