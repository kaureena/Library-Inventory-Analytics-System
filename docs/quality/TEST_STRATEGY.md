# Test Strategy

## Scope
The goal is to validate:
- v1 baseline business rules (issue/return/fines)
- v2 pipeline correctness (row counts, required outputs)
- reproducibility (scripts run on clean machine)

## Test types

### 1) Unit tests (v1)
- validate business rules:
  - cannot issue if stock is 0
  - due date must be after issue date
  - fine only when return date > due date

### 2) Smoke tests (v2)
- ETL runs end-to-end without errors
- curated outputs are written
- dashboard exports exist

### 3) Data Quality tests
- rule checks produce JSON + HTML outputs
- issue register updated for failures/warnings

## Evidence
- Tests live under `v1_bca_basic_system/tests/` and `v2_analytics_modernisation/tests/`
- CI workflows live under `.github/workflows/`
