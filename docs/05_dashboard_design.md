# Dashboard Design

## Page plan
The dashboard pack exports 20 pages as PNG:

See:
- `v2_analytics_modernisation/bi_powerbi/page_index.md`
- `v2_analytics_modernisation/bi_powerbi/exports/`

## Design principles
- One question per page (e.g., “Where are overdues highest?”)
- Prefer KPI cards + 1–3 visuals + table when needed
- Include monitoring pages to show reliability (DQ + refresh health)

## KPI definitions
- Stored in `v2_analytics_modernisation/bi_powerbi/kpi_definitions.csv`

## PBIX build spec
Because the repo avoids unreviewable binary artefacts, the PBIX is represented as a build spec:
- `v2_analytics_modernisation/bi_powerbi/pbix_spec/`
