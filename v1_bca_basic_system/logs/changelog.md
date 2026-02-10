# Changelog — v1 Baseline System

This changelog captures **meaningful milestones** for the **baseline BCA implementation** of the Library Book Inventory & Issue Tracking System.

- **Original Development Period:** Mar–Jun 2010 (Bachelor’s final-year project)
- **Modernisation (Analytics / ETL / Warehouse):** 2025–2026

- **Scope:** Books, Members, Issue/Return, Fines, Overdues, Reports/Exports
- **Storage:** SQLite (OLTP)
- **Evidence:** UI screenshots + sample CSV exports (synthetic)

---

## [1.0.0] — 2010-04-18 (Baseline Release)

### Added
- End-to-end baseline workflow: **Books → Members → Issue/Return → Fines → Exports**
- SQLite schema with constraints and indexes:
  - unique ISBN + member_id
  - guardrails against negative stock
  - audit timestamps
- Synthetic seed data script for portfolio-safe demos
- UI evidence pack (HD screenshots) for all key screens:
  - home, books, add/edit, members, member profile, issue, return, overdues, fines, reports/exports, roles/settings, audit log
- Export pack + register:
  - books, members, issues/returns, fines
- Testing pack:
  - baseline automation tests
  - test matrix + validation rules documentation

### Fixed
- Prevented **double-return** and ensured stock integrity on issue/return paths
- Standardised date formats and fine rounding for exports

---

## [0.8.0] — 2010-04-10 (Runbook + Evidence Round)

### Added
- Step-by-step runbook for evaluators:
  - install, run, demo flow, troubleshooting
- Reproducibility and evidence checks:
  - evidence index links verified
  - screenshots validated as HD and readable

---

## [0.6.0] — 2010-03-28 (Exports + Overdues + Fines)

### Added
- Overdues view with ageing buckets and filters
- CSV exports pack designed to be compatible with v2 analytics
- Fine policy examples added to documentation

---

## [0.4.0] — 2010-03-20 (Issue Workflow)

### Added
- Issue workflow backend (availability checks, due-date policy)
- Issue screen UI + validation messages

---

## [0.2.0] — 2010-03-10  (Books + Schema)

### Added
- Core SQLite schema + seed data draft
- Books CRUD with validation guardrails
- Initial UI menu and Books listing screen

