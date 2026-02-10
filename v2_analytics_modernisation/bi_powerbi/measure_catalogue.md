# Measure Catalogue (Conceptual)

This catalogue explains how key measures would be implemented in BI.

## Measures

### Issues
- **Issues Count** = COUNTROWS(fact_issue_return)

### Returns
- **Returns Count** = COUNTROWS(FILTER(fact_issue_return, returned_flag = 1))

### Overdue Rate
- **Overdues** = SUM(fact_issue_return[overdue_flag])
- **Overdue Rate** = DIVIDE([Overdues], [Returns Count])

### Fine Total
- **Fine Total** = SUM(fact_issue_return[fine_amount])

### Stockout Rate
- **Stockouts** = AVERAGE(kpi_inventory_health[stockout_flag])
  - where stockout_flag = 1 if est_available = 0

## Notes
Exact DAX depends on the chosen data model and relationships.
The repo keeps exports as PNG to remain lightweight and reviewable.
