# Data README (Synthetic)

This repository uses **synthetic data only**.

## Data layers

### v1 (baseline)
- SQLite schema: `v1_bca_basic_system/database/schema.sql`
- Seed script: `v1_bca_basic_system/database/seed_synthetic.sql`
- Export samples: `v1_bca_basic_system/export/`

### v2 (analytics)
- Raw synthetic CSVs: `v2_analytics_modernisation/data/raw/`
- Reference data: `v2_analytics_modernisation/data/reference/`
- Staged outputs: `v2_analytics_modernisation/data_output/staged/`
- Curated outputs: `v2_analytics_modernisation/data_output/curated/`

## Privacy & PII note
- Member names in sample data are **fake** (e.g., `Member_001`).
- No real addresses, phone numbers, emails, or IDs are stored.

## Reproducibility
To regenerate raw data and all outputs:

```bash
cd v2_analytics_modernisation
python scripts/make_sample_data.py
python etl/run_etl.py
python dq_data_quality/run_checks.py
python scripts/generate_bi_exports.py
```
