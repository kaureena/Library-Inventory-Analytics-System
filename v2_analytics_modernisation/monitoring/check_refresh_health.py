from __future__ import annotations
from pathlib import Path
import pandas as pd


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    p = base / "reports/refresh_health_snapshot.csv"
    if not p.exists():
        raise SystemExit("refresh_health_snapshot.csv missing. Run ETL first.")
    df = pd.read_csv(p)
    row = df.iloc[0].to_dict()
    problems = []

    if str(row.get("status", "")).upper() != "OK":
        problems.append("status is not OK")
    if str(row.get("dq_status", "")).upper() == "FAIL":
        problems.append("dq_status is FAIL")
    exp = int(row.get("exports_expected", 0))
    gen = int(row.get("exports_generated", 0))
    if exp and gen < exp:
        problems.append(f"exports_generated {gen} < expected {exp}")

    if problems:
        raise SystemExit("MONITORING FAIL: " + "; ".join(problems))

    print("MONITORING OK:", row)


if __name__ == "__main__":
    main()
