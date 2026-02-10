# v2 Data Dictionary (Key Tables)

## Raw (data/raw)

### books_raw.csv
- book_id (string) — unique ID
- isbn (string) — synthetic ISBN-like
- title, author (string)
- category (string)
- branch (string)
- published_year (int)
- copies_total, copies_available (int)
- acquisition_date (date)
- price (float)

### members_raw.csv
- member_id (string)
- member_name (string) — synthetic
- membership_type (Student/Staff/Public)
- join_date (date)
- status (Active/Inactive)

### transactions_raw.csv
- transaction_id (string)
- member_id (string)
- book_id (string)
- issue_date, due_date, return_date (date)
- fine_amount (float)
- fine_paid (0/1)
- branch (string)

## Curated (data_output/curated)

### fact_issue_return.csv
One row per issue transaction with derived fields:
- returned_flag, overdue_flag
- days_on_loan, days_overdue
- fine_expected, fine_delta

### kpi_inventory_health.csv
Approximate inventory availability at run date:
- on_loan
- est_available
- stockout_flag
