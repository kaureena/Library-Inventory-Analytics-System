# v2 Pipeline Runbook

This is the step-by-step runbook for a reproducible pipeline run.

## 1) Validate environment (optional)
```bash
python scripts/validate_environment.py
```

## 2) Generate raw data
```bash
python scripts/make_sample_data.py
```

Expected raw outputs:
- `data/raw/books_raw.csv`
- `data/raw/members_raw.csv`
- `data/raw/transactions_raw.csv`

## 3) Run ETL
```bash
python etl/run_etl.py
```

Expected staged outputs:
- `data_output/staged/stg_books.csv`
- `data_output/staged/stg_members.csv`
- `data_output/staged/stg_transactions.csv`

Expected curated outputs:
- `data_output/curated/dim_book.csv`
- `data_output/curated/dim_member.csv`
- `data_output/curated/fact_issue_return.csv`
- KPI tables (daily issues/returns, overdues, fines, inventory health, etc.)

Monitoring outputs:
- `reports/run_register_snapshot.csv`
- `reports/refresh_health_snapshot.csv`

## 4) Run DQ checks
```bash
python dq_data_quality/run_checks.py
```

Outputs:
- `reports/dq_summary.json`
- `reports/dq_report.html`
- `logs/V2_DQ_ISSUE_REGISTER.csv` (updated)

## 5) Generate dashboard exports
```bash
python scripts/generate_bi_exports.py
```

Outputs:
- `bi_powerbi/exports/page_*.png`
- `reports/refresh_health_snapshot.csv` updated with exports_generated

## Troubleshooting
- If exports are missing, confirm curated tables exist first.
- If DQ fails, open `dq_report.html` and review failing rules.
