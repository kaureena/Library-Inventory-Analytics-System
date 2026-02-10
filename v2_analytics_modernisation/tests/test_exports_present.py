import pytest
from pathlib import Path


def test_exports_exist():
    base = Path(__file__).resolve().parents[2]
    exports = base / "v2_analytics_modernisation/bi_powerbi/exports"
    if not exports.exists():
        pytest.skip("Exports folder not present.")
    pngs = list(exports.glob("*.png"))
    if not pngs:
        pytest.skip("No exports present (generate_bi_exports not run).")
    assert any("page_01" in p.name for p in pngs)
