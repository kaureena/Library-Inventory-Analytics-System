# v2 Process Log

## Objective
Transform baseline library data into an analytics-ready dataset and dashboards.

## Pipeline stages
1. **Raw generation** (`scripts/make_sample_data.py`)
   - creates books, members, transactions as CSV
2. **ETL** (`etl/run_etl.py`)
   - produces staged outputs (clean tables)
   - produces curated outputs (dims/facts + KPI tables)
   - writes monitoring snapshots
3. **DQ checks** (`dq_data_quality/run_checks.py`)
   - validates business rules (due dates, fine logic, referential integrity)
   - produces JSON + HTML report
   - updates DQ issue register
4. **Dashboard exports** (`scripts/generate_bi_exports.py`)
   - generates Power BI-style dashboard page PNGs from curated tables

## Evidence
- Curated outputs: `data_output/curated/`
- DQ report: `reports/dq_report.html`
- Dashboard exports: `bi_powerbi/exports/`
