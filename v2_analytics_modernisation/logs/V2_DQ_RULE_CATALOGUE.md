# v2 Data Quality Rule Catalogue

This catalogue defines the rules enforced by `dq_data_quality/run_checks.py`.

## Rule list

| Rule ID | Severity | Description | Example failure |
|---|---|---|---|
| required_columns | FAIL | Staged tables must include required columns | missing `book_id` |
| unique_ids | FAIL | book_id, member_id, transaction_id must be unique | duplicate transaction_id |
| referential_integrity | FAIL | transactions must reference valid book_id and member_id | unknown member_id |
| due_date_after_issue_date | WARN | due_date must be after issue_date | due_date == issue_date |
| return_after_issue_date | FAIL | return_date cannot be before issue_date | negative loan length |
| fine_only_when_overdue | WARN | fine_amount must be 0 unless return_date > due_date | fine charged early |
| fine_matches_overdue_days | WARN | fine_amount should match days_overdue * fine_per_day | mismatch due to rounding |
| stock_sane | FAIL | copies_available between 0 and copies_total | negative stock |
| refresh_snapshot_present | INFO/WARN | refresh snapshot should exist after ETL | missing snapshot file |

## Why WARN vs FAIL?
- WARN rules indicate “data smells” that need review but might be tolerable (e.g., rounding deltas).
- FAIL rules indicate broken data integrity (e.g., referential violations, impossible dates).
