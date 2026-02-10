# BI Layer (Exports + PBIX Spec)

This repository prioritises **reviewable evidence**.

## What is included

### 1) Real dashboard evidence (PNG)
- `exports/page_*.png` — 20 dashboard pages
- `page_index.md` — page list + purpose

### 2) Content-rich PBIX build specification (text)
Instead of a binary `.pbix` file, we include a reproducible spec:
- `pbix_spec/README.md` — rebuild instructions
- `pbix_spec/model_relationships.md` — star schema relationships
- `pbix_spec/dax_measures.dax` — measure list
- `pbix_spec/visual_inventory.md` — page-by-page visuals
- `pbix_spec/theme.json` — optional theme

This prevents “unreviewable binary files” while keeping the BI layer fully auditable.
