# Risk & Issues Log — v2 Analytics Modernisation

This log tracks risks/issues encountered while building the analytics layer (ETL + DQ + dashboards + monitoring).

| ID | Risk / Issue | Impact | Mitigation | Owner | Status | Opened | Closed | Notes |
|---|---|---|---|---|---|---|---|---|
| R1 | Synthetic generator drift vs v1 business rules | DQ failures; inconsistent KPIs | Keep rules in one place; document assumptions; add DQ checks for policy invariants | Data | Closed | 2026-01-19 | 2026-01-23 | Generator aligned to due-date and fine policy |
| R2 | ETL not idempotent (re-runs overwrite incorrectly) | Broken refresh; inconsistent dashboards | Add run_id, atomic writes, deterministic sorting; smoke tests | ETL | Closed | 2026-01-21 | 2026-01-30 | Added idempotency checks + fixed ordering |
| R3 | DQ rules too strict (false positives) | Noise in issue register; confusion | Start with “critical” rules; classify severity; document limitations | DQ | Open | 2026-01-23 |  | Low-severity rules flagged as “Advisory” |
| R4 | Monitoring tables not populated consistently | Broken monitoring dashboards | Generate monitoring snapshots at end of ETL run; validate row counts | Ops | Closed | 2026-01-28 | 2026-02-02 | Refresh history and run register validated |
| R5 | Dashboard pages mismatch curated table grain | Wrong aggregations; misleading visuals | KPI definition catalogue; ensure each page maps to curated table grain | BI | Closed | 2026-01-26 | 2026-01-31 | Added page plan + KPI definitions |
| R6 | File size bloat for PNG exports | Repo heavy; slower reviews | Use consistent resolution and compression; keep PNGs readable but not huge | BI | Closed | 2026-01-26 | 2026-01-31 | Standardised export size across pages |
| R7 | DQ report format not human-readable | Hard for evaluators to review | Provide JSON summary + HTML report; add runbook pointers | DQ | Closed | 2026-01-23 | 2026-02-02 | HTML report added; linked in README |
| R8 | Refresh cadence unclear | Reviewer confusion | Document refresh cadence (demo schedule) and how to trigger run locally | PM | Closed | 2026-01-25 | 2026-02-02 | Monitoring playbook updated |
| R9 | Tests missing coverage for dashboards presence | CI passes while exports missing | Add exports presence tests + file count checks | Test | Closed | 2026-01-30 | 2026-01-30 | test_exports_present added |
| R10 | Incomplete documentation for end-to-end run | Hard to reproduce | Add run_all_local scripts + step-by-step pipeline runbook | Doc | Closed | 2026-02-01 | 2026-02-02 | Runbook improved and validated |

