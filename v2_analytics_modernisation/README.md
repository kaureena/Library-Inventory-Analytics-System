# v2 — Analytics Modernisation

v2 turns the baseline library workflow into an analytics-ready platform:

- synthetic raw data generation
- ETL (raw → staged → curated)
- data quality checks with reports
- warehouse/star schema SQL artefacts
- dashboard exports (Power BI-style PNG)
- monitoring snapshots (run register + refresh health)

## Quick run
```bash
pip install -r requirements.txt
python scripts/make_sample_data.py
python etl/run_etl.py
python dq_data_quality/run_checks.py
python scripts/generate_bi_exports.py
```

## Key folders
- `data/raw/` — raw synthetic CSVs
- `data_output/staged/` — cleaned staging outputs
- `data_output/curated/` — KPI tables + dim/fact style outputs
- `reports/` — DQ summary + HTML report + refresh snapshots
- `bi_powerbi/exports/` — PNG exports of dashboards
- `logs/` — process log + runbook + DQ catalogue + data dictionary
