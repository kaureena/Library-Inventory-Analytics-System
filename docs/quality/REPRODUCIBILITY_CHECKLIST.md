# Reproducibility Checklist

Use this checklist before sharing or submitting the repo.

## Hygiene
- [ ] No `.git/` folder included in a ZIP upload
- [ ] No `__pycache__/` or `*.pyc`
- [ ] No secrets committed (`.env.example` only)
- [ ] Data is synthetic only

## End-to-end run
- [ ] `python scripts/make_sample_data.py` runs cleanly
- [ ] `python etl/run_etl.py` produces staged + curated outputs
- [ ] `python dq_data_quality/run_checks.py` produces JSON + HTML
- [ ] `python scripts/generate_bi_exports.py` produces PNG exports

## Evidence
- [ ] Dashboard PNG exports open in standard image viewers
- [ ] v1 UI screenshots open and are readable (1920×1080 recommended)
- [ ] README links to screenshots resolve correctly
