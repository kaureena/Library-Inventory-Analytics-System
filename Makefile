.PHONY: v2-run v2-dq v2-bi test lint

v2-run:
	cd v2_analytics_modernisation && python scripts/make_sample_data.py && python etl/run_etl.py

v2-dq:
	cd v2_analytics_modernisation && python dq_data_quality/run_checks.py

v2-bi:
	cd v2_analytics_modernisation && python scripts/generate_bi_exports.py

test:
	pytest -q

lint:
	python -m compileall -q .
