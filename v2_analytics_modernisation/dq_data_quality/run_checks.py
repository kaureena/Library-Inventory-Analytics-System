"""Run data quality checks for the library analytics pipeline.

Reads staged + curated outputs and writes:
- reports/dq_summary.json
- reports/dq_report.html
- logs/V2_DQ_ISSUE_REGISTER.csv (append/update)

The aim is to demonstrate a realistic DQ gate in a portfolio project.
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
import json
import pandas as pd
import numpy as np


def _now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat(sep=" ")


def _result(
    rule_id: str,
    description: str,
    severity: str,
    status: str,
    fail_rows: int = 0,
    sample_keys: list[str] | None = None,
    notes: str = "",
) -> dict:
    return {
        "rule_id": rule_id,
        "description": description,
        "severity": severity,  # INFO/WARN/FAIL
        "status": status,  # PASS/WARN/FAIL
        "fail_rows": int(fail_rows),
        "sample_keys": sample_keys or [],
        "notes": notes,
    }


def main() -> None:
    base = Path(__file__).resolve().parents[1]  # v2_analytics_modernisation
    staged = base / "data_output/staged"
    reports = base / "reports"
    logs_dir = base / "logs"

    run_time = _now_iso()

    # Load staged tables
    books = pd.read_csv(staged / "stg_books.csv")
    members = pd.read_csv(staged / "stg_members.csv")
    tx = pd.read_csv(
        staged / "stg_transactions.csv",
        parse_dates=["issue_date", "due_date", "return_date"],
    )

    results: list[dict] = []

    # Rule: required columns
    required_books = {
        "book_id",
        "title",
        "author",
        "category",
        "branch",
        "copies_total",
        "copies_available",
    }
    required_members = {
        "member_id",
        "member_name",
        "membership_type",
        "join_date",
        "status",
    }
    required_tx = {
        "transaction_id",
        "member_id",
        "book_id",
        "issue_date",
        "due_date",
        "return_date",
        "fine_amount",
        "fine_paid",
    }

    missing = sorted(list(required_books - set(books.columns)))
    missing += sorted(list(required_members - set(members.columns)))
    missing += sorted(list(required_tx - set(tx.columns)))
    if missing:
        results.append(
            _result(
                "required_columns",
                "Required columns must exist in staged tables",
                "FAIL",
                "FAIL",
                fail_rows=len(missing),
                notes="Missing: " + ",".join(missing),
            )
        )
    else:
        results.append(
            _result(
                "required_columns",
                "Required columns must exist in staged tables",
                "INFO",
                "PASS",
            )
        )

    # Rule: unique IDs
    dup_books = int(books["book_id"].duplicated().sum())
    dup_members = int(members["member_id"].duplicated().sum())
    dup_tx = int(tx["transaction_id"].duplicated().sum())
    dup_total = dup_books + dup_members + dup_tx
    if dup_total > 0:
        results.append(
            _result(
                "unique_ids",
                "Primary keys should be unique",
                "FAIL",
                "FAIL",
                fail_rows=dup_total,
            )
        )
    else:
        results.append(
            _result("unique_ids", "Primary keys should be unique", "INFO", "PASS")
        )

    # Rule: referential integrity
    bad_book = (
        tx.loc[~tx["book_id"].isin(set(books["book_id"])), "transaction_id"]
        .head(5)
        .tolist()
    )
    bad_member = (
        tx.loc[~tx["member_id"].isin(set(members["member_id"])), "transaction_id"]
        .head(5)
        .tolist()
    )
    bad_total = len(bad_book) + len(bad_member)
    if bad_total > 0:
        results.append(
            _result(
                "referential_integrity",
                "Transactions must reference valid book_id and member_id",
                "FAIL",
                "FAIL",
                fail_rows=bad_total,
                sample_keys=bad_book + bad_member,
            )
        )
    else:
        results.append(
            _result(
                "referential_integrity",
                "Transactions must reference valid book_id and member_id",
                "INFO",
                "PASS",
            )
        )

    # Rule: due_date > issue_date (warn)
    bad_due = (
        tx.loc[tx["due_date"] <= tx["issue_date"], "transaction_id"].head(10).tolist()
    )
    if bad_due:
        results.append(
            _result(
                "due_date_after_issue_date",
                "Due date must be after issue date",
                "WARN",
                "WARN",
                fail_rows=len(bad_due),
                sample_keys=bad_due,
            )
        )
    else:
        results.append(
            _result(
                "due_date_after_issue_date",
                "Due date must be after issue date",
                "INFO",
                "PASS",
            )
        )

    # Rule: return_date >= issue_date (fail if violated)
    bad_return = (
        tx.dropna(subset=["return_date"])
        .loc[tx["return_date"] < tx["issue_date"], "transaction_id"]
        .head(10)
        .tolist()
    )
    if bad_return:
        results.append(
            _result(
                "return_after_issue_date",
                "Return date cannot be before issue date",
                "FAIL",
                "FAIL",
                fail_rows=len(bad_return),
                sample_keys=bad_return,
            )
        )
    else:
        results.append(
            _result(
                "return_after_issue_date",
                "Return date cannot be before issue date",
                "INFO",
                "PASS",
            )
        )

    # Rule: fine only when overdue (warn)
    fine_not_overdue = (
        tx.dropna(subset=["return_date"])
        .loc[
            (tx["fine_amount"] > 0) & (tx["return_date"] <= tx["due_date"]),
            "transaction_id",
        ]
        .head(10)
        .tolist()
    )
    if fine_not_overdue:
        results.append(
            _result(
                "fine_only_when_overdue",
                "Fine can be charged only if return_date > due_date",
                "WARN",
                "WARN",
                fail_rows=len(fine_not_overdue),
                sample_keys=fine_not_overdue,
            )
        )
    else:
        results.append(
            _result(
                "fine_only_when_overdue",
                "Fine can be charged only if return_date > due_date",
                "INFO",
                "PASS",
            )
        )

    # Rule: fine matches overdue days (warn)
    fine_expected = np.round(tx["days_overdue"] * 1.0, 2)
    delta = np.round(tx["fine_amount"] - fine_expected, 2)
    bad_delta = tx.loc[delta.abs() > 0.01, "transaction_id"].head(10).tolist()
    if bad_delta:
        results.append(
            _result(
                "fine_matches_overdue_days",
                "Fine amount should match days_overdue * fine_per_day",
                "WARN",
                "WARN",
                fail_rows=len(bad_delta),
                sample_keys=bad_delta,
            )
        )
    else:
        results.append(
            _result(
                "fine_matches_overdue_days",
                "Fine amount should match days_overdue * fine_per_day",
                "INFO",
                "PASS",
            )
        )

    # Rule: stock columns sane (fail if violated)
    bad_stock = (
        books.loc[
            (books["copies_total"] < 0)
            | (books["copies_available"] < 0)
            | (books["copies_available"] > books["copies_total"]),
            "book_id",
        ]
        .head(10)
        .tolist()
    )
    if bad_stock:
        results.append(
            _result(
                "stock_sane",
                "copies_available must be between 0 and copies_total",
                "FAIL",
                "FAIL",
                fail_rows=len(bad_stock),
                sample_keys=bad_stock,
            )
        )
    else:
        results.append(
            _result(
                "stock_sane",
                "copies_available must be between 0 and copies_total",
                "INFO",
                "PASS",
            )
        )

    # Rule: refresh snapshot exists (info)
    refresh_path = reports / "refresh_health_snapshot.csv"
    if not refresh_path.exists():
        results.append(
            _result(
                "refresh_snapshot_present",
                "Refresh snapshot must exist after ETL",
                "WARN",
                "WARN",
                fail_rows=1,
            )
        )
    else:
        results.append(
            _result(
                "refresh_snapshot_present",
                "Refresh snapshot must exist after ETL",
                "INFO",
                "PASS",
            )
        )

    warn_count = sum(1 for r in results if r["status"] == "WARN")
    fail_count = sum(1 for r in results if r["status"] == "FAIL")

    overall = "PASS"
    if fail_count > 0:
        overall = "FAIL"
    elif warn_count > 0:
        overall = "PASS_WITH_WARNINGS"

    summary = {
        "run_time": run_time,
        "overall_status": overall,
        "warn_rules": warn_count,
        "fail_rules": fail_count,
        "rules": results,
    }

    reports.mkdir(parents=True, exist_ok=True)
    (reports / "dq_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    # HTML report (simple)
    rows_html = ""
    for r in results:
        rows_html += f"<tr><td>{r['rule_id']}</td><td>{r['severity']}</td><td>{r['status']}</td><td>{r['fail_rows']}</td><td>{', '.join(r['sample_keys'][:5])}</td><td>{r['description']}</td></tr>\n"

    html = f"""<!doctype html>
<html>
<head>
  <meta charset='utf-8'/>
  <title>DQ Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; }}
    .badge {{ display:inline-block; padding:4px 10px; border-radius:14px; background:#eee; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; font-size: 13px; }}
    th {{ background: #f4f4f4; text-align: left; }}
  </style>
</head>
<body>
  <h1>Data Quality Report — Library Pipeline</h1>
  <p>Run time: <b>{run_time}</b></p>
  <p>Overall status: <span class='badge'><b>{overall}</b></span></p>

  <h2>Rule results</h2>
  <table>
    <thead>
      <tr><th>Rule</th><th>Severity</th><th>Status</th><th>Fail rows</th><th>Sample keys</th><th>Description</th></tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>

  <p style="margin-top:16px;color:#666;">
    This report is generated from synthetic data for portfolio purposes.
  </p>
</body>
</html>
"""
    (reports / "dq_report.html").write_text(html, encoding="utf-8")

    # Update DQ issue register (append WARN/FAIL)
    issue_path = logs_dir / "V2_DQ_ISSUE_REGISTER.csv"
    issue_path.parent.mkdir(parents=True, exist_ok=True)
    if not issue_path.exists():
        issue_path.write_text(
            "issue_id,run_time,rule_id,severity,status,sample_key,notes\n",
            encoding="utf-8",
        )

    existing = pd.read_csv(issue_path)
    new_rows = []
    seq_start = len(existing) + 1

    for r in results:
        if r["status"] in ("WARN", "FAIL"):
            sample = r["sample_keys"][0] if r["sample_keys"] else ""
            new_rows.append(
                {
                    "issue_id": f"DQ-{seq_start:04d}",
                    "run_time": run_time,
                    "rule_id": r["rule_id"],
                    "severity": r["severity"],
                    "status": r["status"],
                    "sample_key": sample,
                    "notes": r["description"],
                }
            )
            seq_start += 1

    if new_rows:
        updated = pd.concat([existing, pd.DataFrame(new_rows)], ignore_index=True)
    else:
        updated = existing

    updated.to_csv(issue_path, index=False)

    # Update refresh snapshot dq_status
    if refresh_path.exists():
        snap = pd.read_csv(refresh_path)
        snap.loc[0, "dq_status"] = overall
        snap.loc[0, "dq_checked_time"] = run_time
        snap.to_csv(refresh_path, index=False)

    print("DQ complete.")
    print("Summary:", reports / "dq_summary.json")
    print("Report:", reports / "dq_report.html")


if __name__ == "__main__":
    main()
