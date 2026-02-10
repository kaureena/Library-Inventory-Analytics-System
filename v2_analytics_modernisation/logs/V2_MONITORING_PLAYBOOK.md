# V2 Monitoring Playbook

This playbook explains how to **monitor** the v2 pipeline (raw → staged → curated → dashboards) in a portfolio-safe repo.

> Monitoring is deliberately lightweight: it is designed to be **credible** and **reviewable**, not production-grade.

---

## What “healthy” looks like

A healthy run should produce:

1. **Staged outputs** in `data_output/staged/`
2. **Curated outputs** in `data_output/curated/`
3. **DQ reports**
   - `reports/dq_summary.json`
   - `reports/dq_report.html`
4. **BI exports** in `bi_powerbi/exports/`
5. **Monitoring records**
   - `logs/V2_RUN_REGISTER.csv`
   - `logs/V2_REFRESH_HISTORY.csv`
   - `logs/V2_DQ_ISSUE_REGISTER.csv`

---

## Key monitoring artefacts

### 1) Run Register (`logs/V2_RUN_REGISTER.csv`)
A single-row-per-run register capturing:
- `run_id`
- run timestamp
- row counts (raw/staged/curated)
- DQ pass rate
- duration (seconds)

**How to use it**
- Confirm each run has a unique `run_id`
- Confirm row counts are within expected bounds
- Confirm DQ pass rate is not unexpectedly low

### 2) Refresh History (`logs/V2_REFRESH_HISTORY.csv`)
A time series that allows:
- trend analysis
- detection of “row count drift”
- detection of refresh gaps

**How to use it**
- Look for missing days (if running daily)
- Look for sudden spikes/drops in curated tables

### 3) DQ Issue Register (`logs/V2_DQ_ISSUE_REGISTER.csv`)
The audit trail of data quality exceptions:
- `rule_id`
- severity (critical/advisory)
- sample offending keys
- first_seen/last_seen

**How to use it**
- Critical issues should usually be **0** for a “green” demo run
- Advisory issues can remain to show realism (documented in runbook)

---

## Operational cadence (portfolio demo)

Suggested demo cadence:
- Run pipeline whenever you need fresh screenshots/evidence:
  - before updating README
  - before packaging a release zip

Minimum recommended:
- At least one clean run with **DQ pass = green** before final submission.

---

## Quick checklist (before sharing repo)

- [ ] DQ report opens in browser (HTML) and summary JSON is readable
- [ ] Dashboard page count matches `bi_powerbi/page_index.md` (20 pages)
- [ ] Run register has the latest run_id
- [ ] Evidence index links to exports and reports correctly

---

## Common failure modes & fixes

### DQ failures: impossible dates
- Symptom: rule flags `return_date < issue_date`
- Fix: check generator logic and ETL type casting; re-run generator with deterministic seed

### Row count drift
- Symptom: staged counts drop by large % unexpectedly
- Fix: confirm dedupe keys; ensure ETL isn’t dropping valid records due to null handling

### Missing BI exports
- Symptom: some pages not generated
- Fix: re-run `scripts/generate_bi_exports.py`; verify curated tables exist

