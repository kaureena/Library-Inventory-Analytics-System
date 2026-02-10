# Changelog — v2 Analytics Modernisation

This changelog captures **meaningful milestones** for the **analytics modernisation layer** built on top of the baseline library system.

- **Scope:** Synthetic raw → ETL → Data Quality gate → curated outputs → warehouse-ready model → dashboard exports + monitoring
- **Data:** Synthetic only (portfolio-safe)

---

## [2.0.0] — 2026-02-03 (Analytics Release)

### Added
- Synthetic data generator (raw CSV): books, members, transactions (multi-branch + categories)
- ETL pipeline:
  - raw → staged (cleaning, typing, dedupe)
  - staged → curated (dims/facts + KPI tables)
  - run_id + row-count snapshots
- Data Quality gate:
  - rule catalogue aligned to business logic (dates, stock, fine logic, referential integrity)
  - outputs: dq_summary.json + dq_report.html
  - DQ issue register for auditability
- Warehouse-ready star schema SQL artefacts (dims/facts) for BI modelling
- Dashboard export pack (Power BI-style PNG):
  - **20 pages** (overview, operational KPIs, DQ & monitoring pages, drill-through)
  - page_index.md + KPI definition catalogue
- Monitoring pack:
  - run register, refresh history, health drift checks (row counts + DQ pass rate)
- Tests:
  - ETL smoke, DQ smoke, exports presence checks

### Fixed
- Idempotency: pipeline can run multiple times without breaking outputs
- Dashboard consistency: ensured all pages map to curated tables and documented KPIs

---

## [1.3.0] — 2026-01-31 (Dashboards Completed)

### Added
- Completed dashboard pages 16–20:
  - ETL run history, refresh health monitoring, what-if policy, drill-through book profile, KPI definitions

---

## [1.1.0] — 2026-01-23 (DQ Gate)

### Added
- Rule catalogue + first pass DQ checks
- JSON + HTML reporting for portfolio evidence

---

## [1.0.0] — 2026-01-19 (v2 Kickoff)

### Added
- KPI catalogue and dashboard page plan
- v2 folder structure scaffold and documentation outline

