# Architecture

## Why two versions?

This repository is intentionally split:

- **v1** proves the BCA-level operational workflow (CRUD + exports)
- **v2** proves analytics engineering practices (ETL + DQ + warehouse + dashboards)

This prevents “over-claiming” and makes the story credible.

---

## v1 (Baseline system)

**Goal:** record operational events in a small OLTP store.

Key components:
- UI forms for Books/Members/Issue-Return/Fines/Reports
- SQLite schema + seed data
- CSV exports as evidence

---

## v2 (Analytics modernisation)

**Goal:** generate trusted analytical datasets and dashboards.

Pipeline:
1. Generate synthetic raw CSVs (`scripts/make_sample_data.py`)
2. ETL (raw → staged → curated) (`etl/run_etl.py`)
3. Data Quality checks + reports (`dq_data_quality/run_checks.py`)
4. Dashboard exports (PNG) (`scripts/generate_bi_exports.py`)

Outputs:
- Curated KPI tables
- Run register + refresh history
- “Power BI-style” dashboard exports for portfolio review

---

## Diagrams
- Mermaid sources: `docs/mermaid/`
- PNG diagrams: `docs/diagrams/`
