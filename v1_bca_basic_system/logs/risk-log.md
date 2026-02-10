# Risk & Issues Log — v1 Baseline

This log tracks risks/issues encountered while building the baseline Library Book Inventory & Issue Tracking System.

| ID | Risk / Issue | Impact | Mitigation | Owner | Status | Opened | Closed | Notes |
|---|---|---|---|---|---|---|---|---|
| R1 | Accidental PII in demo data | Privacy breach; portfolio risk | Use **synthetic names/IDs** only; add privacy checklist; review exports before commit | Data | Closed | 2010-03-10 | 2010-03-28 | Confirmed no real identities; documented in PRIVACY.md |
| R2 | Negative stock due to bad issue/return logic | Inventory numbers wrong; credibility loss | Stock guardrails; validate availability before issue; prevent double return | Dev | Closed | 2010-03-11 | 2010-03-31 | Fixed by enforcing atomic updates + checks |
| R3 | Duplicate ISBN or member_id collisions | CRUD failures; incorrect records | Add UNIQUE constraints; validate on input; test with seed data | DB | Closed | 2010-03-04 | 2010-03-13 | Schema constraints verified via tests |
| R4 | Fine policy ambiguity (rounding, grace days) | Incorrect fine totals; disputes | Write explicit fine policy examples; encode in rules.py; add tests | Product | Closed | 2010-03-17 | 2010-04-06 | Documented in README + validation rules |
| R5 | Export files not matching UI counts | Evidence inconsistency; reviewer confusion | Export register; verification checklist; QA pass after each export update | QA | Closed | 2010-03-26 | 2010-04-10 | Export register updated; counts reconciled |
| R6 | Date parsing inconsistencies across OS locales | Wrong due dates/fines | Enforce ISO dates; validate parsing; test for edge dates | Dev | Closed | 2010-03-22 | 2010-03-31 | Standardised ISO 8601 in exports |
| R7 | UI allows invalid inputs (empty title, negative copies) | Data corruption; runtime errors | Field-level validation; disable submit until valid; error messages | UI | Closed | 2010-03-12 | 2010-04-13 | UI polish + validation messages |
| R8 | Missing auditability of actions | Hard to explain changes; less professional | Add simple audit log output; document in runbook | Dev | Closed | 2010-03-30 | 2010-04-03 | Audit view screenshot captured |
| R9 | Tests become flaky due to random seed changes | Unreliable CI results | Use deterministic seed data; keep fixtures stable | Test | Closed | 2010-04-05 | 2010-04-07 | Fixtures frozen after regression |
| R10 | Scope creep (extra features vs stability) | Delays; low quality | Prioritise correctness + evidence; keep “nice-to-have” features clearly marked | PM | Closed | 2010-03-06 | 2010-04-17 | Maintained strict baseline scope |

