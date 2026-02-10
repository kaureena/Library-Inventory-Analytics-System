# Install / Run Steps

## Option A: Run the v2 pipeline (recommended)
```bash
cd v2_analytics_modernisation
pip install -r requirements.txt
python scripts/make_sample_data.py
python etl/run_etl.py
python dq_data_quality/run_checks.py
python scripts/generate_bi_exports.py
```

## Option B: Run the v1 baseline demo (simple)
```bash
cd v1_bca_basic_system
pip install -r requirements.txt
python src/main.py
```

## Notes
- This repo uses synthetic data only.
- Use the generated screenshots under `docs/screenshots/` for a quick “proof of run”.
