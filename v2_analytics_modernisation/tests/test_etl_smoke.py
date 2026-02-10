import pytest
from pathlib import Path
import pandas as pd


def test_curated_outputs_exist():
    base = Path(__file__).resolve().parents[2]
    curated = base / "v2_analytics_modernisation/data_output/curated"
    if not curated.exists():
        pytest.skip("Curated outputs not present (ETL not run).")
    required = [
        "dim_book.csv",
        "dim_member.csv",
        "fact_issue_return.csv",
        "kpi_daily_issues_returns.csv",
    ]
    for r in required:
        assert (curated / r).exists(), f"Missing {r}"


def test_fact_issue_return_columns():
    base = Path(__file__).resolve().parents[2]
    p = base / "v2_analytics_modernisation/data_output/curated/fact_issue_return.csv"
    if not p.exists():
        pytest.skip("fact_issue_return not present (ETL not run).")
    df = pd.read_csv(p, nrows=5)
    for col in [
        "transaction_id",
        "member_id",
        "book_id",
        "issue_date",
        "due_date",
        "fine_amount",
        "overdue_flag",
    ]:
        assert col in df.columns
