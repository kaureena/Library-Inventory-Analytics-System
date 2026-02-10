# v1 — Baseline Library System (BCA)

v1 is a simple baseline workflow system to demonstrate BCA-level capability:

- manage **books**
- manage **members**
- record **issue/return**
- calculate **fines**
- generate **CSV exports**
- provide **UI screenshots** as proof

This version is intentionally simple and focused on correctness and business rules.

## Run (demo)

```bash
pip install -r requirements.txt
python src/main.py
```

## Evidence
- UI: `ui/screenshots/`
- Schema: `database/schema.sql`
- Seed: `database/seed_synthetic.sql`
- Exports: `export/`
- Logs: `logs/`
