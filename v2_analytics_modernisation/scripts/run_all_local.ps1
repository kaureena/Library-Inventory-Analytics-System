python scripts/make_sample_data.py
python etl/run_etl.py
python dq_data_quality/run_checks.py
python scripts/generate_bi_exports.py
Write-Output "All done."
