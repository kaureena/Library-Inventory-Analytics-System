# PBIX Build Specification (Content-Rich Alternative)

This repository stores **reviewable dashboard exports** as PNG files under `../exports/`.

To keep the repo fully text-reviewable (and to avoid unreviewable binary files), we include a **PBIX build spec** instead of committing a `.pbix` file.

## How to rebuild the PBIX (high level)

1. Open Power BI Desktop
2. **Get Data → Text/CSV** and load curated tables from:
   - `v2_analytics_modernisation/data_output/curated/`
3. Create relationships described in `model_relationships.md`
4. Add measures from `dax_measures.dax`
5. Build pages using `visual_inventory.md`
6. Optional: apply theme `theme.json`

This approach is:
- transparent (reviewers can read the model and DAX)
- reproducible (tables come from the ETL scripts)
- portfolio-safe (no hidden binaries)
