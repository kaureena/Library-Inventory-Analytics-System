# Data Quality Strategy

## Why DQ matters for a library workflow
A library system is audit-sensitive:
- you must know which member has which book
- you must not issue stock that does not exist
- you must calculate fines consistently

## DQ layers
- **Schema/required fields:** required columns present, types valid
- **Referential integrity:** transactions reference valid members + books
- **Business rules:** due_date after issue_date, no negative stock, fine logic
- **Freshness:** refresh snapshot exists with last_run_time

## Outputs
- Summary JSON: `v2_analytics_modernisation/reports/dq_summary.json`
- HTML report: `v2_analytics_modernisation/reports/dq_report.html`
- DQ issue register: `v2_analytics_modernisation/logs/V2_DQ_ISSUE_REGISTER.csv`
