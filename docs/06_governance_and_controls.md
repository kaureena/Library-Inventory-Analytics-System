# Governance and Controls

## Data controls
- Synthetic data only
- No secrets committed (`.env.example` only)
- Logs are sanitised

## Process controls (portfolio)
- Run register + refresh snapshot
- DQ rule catalogue + issue register
- CI workflows (tests + ETL smoke + DQ)

## Evidence controls
- High-resolution screenshots for:
  - v1 UI
  - v2 dashboards
  - pipeline steps
- Evidence packs stored under `docs/evidence/`
