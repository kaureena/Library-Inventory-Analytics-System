# Reference File Structure

This file explains **why each folder exists** and how it supports the portfolio story:

- **v1_bca_basic_system/**: baseline operational system (CRUD + exports + UI proof)
- **v2_analytics_modernisation/**: analytics platform (ETL + DQ + warehouse + dashboards)
- **docs/**: content-rich design notes + governance logs + diagrams + evidence packs
- **logs/**: safe sample runtime logs (no secrets)

## High-level tree

```text
Library-Book-Inventory-Issue-Tracking-System/
  README.md
  ARCHITECTURE.md
  EVIDENCE_INDEX.md
  REFERENCE_FILE_STRUCTURE.md
  docs/
    00_context_and_objective.md
    01_requirements_and_user_stories.md
    02_process_flows.md
    03_data_model.md
    04_etl_design.md
    05_dashboard_design.md
    06_governance_and_controls.md
    07_future_enhancements.md
    logs/        (governance pack 00–09)
    quality/     (test + DQ + reproducibility)
    mermaid/     (diagram sources)
    diagrams/    (PNG diagrams)
    screenshots/ (README step screenshots)
    evidence/    (evidence packs)
  v1_bca_basic_system/
    ui/screenshots/
    export/
    database/
    src/
    tests/
    logs/
  v2_analytics_modernisation/
    data/raw/
    data_output/staged/
    data_output/curated/
    etl/
    dq_data_quality/
    warehouse/
    bi_powerbi/
      exports/
      pbix_spec/
    reports/
    monitoring/
    api_service/
    tests/
```

## Naming conventions

- **Run IDs:** `run-0001`, `run-0002` … (see `docs/logs/05_run_register.csv`)
- **Dashboards:** `bi_powerbi/exports/page_XX_XX_*.png`
- **Evidence screenshots:** `docs/evidence/<area>/evidence_XX_*.png`

Updated: 2026-02-03
