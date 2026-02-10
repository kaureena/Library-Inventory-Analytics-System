# ETL Design

## Raw → Staged
**Goal:** make tables analysis-ready.

### books_raw → stg_books
Transformations:
- type casting: copies_total/copies_available to int
- sanity checks: available <= total

### members_raw → stg_members
Transformations:
- status default to Active where missing
- join_date parsing

### transactions_raw → stg_transactions
Transformations:
- date parsing: issue/due/return
- derived fields:
  - returned_flag
  - days_on_loan
  - days_overdue (clipped to >= 0)
  - overdue_flag
  - fine_expected, fine_delta

## Staged → Curated
**Goal:** create reporting datasets.

- dim_book from stg_books
- dim_member from stg_members
- fact_issue_return joins transaction + book attributes
- fact_fines subset where fine_amount > 0

KPI tables:
- daily issues/returns
- overdue daily
- fines weekly
- inventory health (approx)
- category insights
- member activity top
- branch comparison
- overdue ageing buckets

## Monitoring
Snapshots:
- run_register_snapshot.csv
- refresh_health_snapshot.csv

These support pipeline confidence and dashboard completeness checks.
