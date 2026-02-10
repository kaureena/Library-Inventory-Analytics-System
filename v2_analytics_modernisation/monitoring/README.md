# Monitoring (Portfolio)

Monitoring here is implemented as lightweight CSV snapshots + a simple checker.

## Outputs
- `reports/run_register_snapshot.csv`
- `reports/refresh_health_snapshot.csv`

## Checker
Run:

```bash
python monitoring/check_refresh_health.py
```

It will validate:
- last refresh time exists
- dq_status is not FAIL
- expected number of exports were generated
