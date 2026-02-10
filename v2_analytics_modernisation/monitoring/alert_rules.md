# Alert Rules (Concept)

This file documents the alerting logic that would exist in a production setting.

## Alerts
1. **DQ Failure**
   - Trigger: dq_status == FAIL
   - Impact: dashboards may be unreliable
2. **Exports Missing**
   - Trigger: exports_generated < exports_expected
   - Impact: dashboard pack incomplete
3. **Stale Refresh**
   - Trigger: last_refresh_time older than threshold (e.g., 24h)
   - Impact: data is stale
