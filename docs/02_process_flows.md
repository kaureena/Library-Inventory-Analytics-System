# Process Flows

## Issue flow

```mermaid
flowchart TD
  A[Select Member] --> B{Member Active?}
  B -->|No| X[Block Issue + Show Message]
  B -->|Yes| C[Select Book]
  C --> D{copies_available > 0?}
  D -->|No| Y[Block Issue + Stockout Message]
  D -->|Yes| E[Set issue_date + due_date]
  E --> F{due_date > issue_date?}
  F -->|No| Z[Block Issue + Date Validation]
  F -->|Yes| G[Create transaction]
  G --> H[Decrement copies_available]
  H --> I[Export/Audit Log]
```

## Return flow

```mermaid
flowchart TD
  A[Search transaction] --> B[Enter return_date]
  B --> C{return_date >= issue_date?}
  C -->|No| X[Block Return + Validation]
  C -->|Yes| D{return_date > due_date?}
  D -->|No| E[Fine = 0]
  D -->|Yes| F[Fine = days_overdue × fine_per_day]
  E --> G[Update transaction as returned]
  F --> G
  G --> H[Increment copies_available]
  H --> I[Optional fine payment]
```

## Export flow (v1 → v2)

```mermaid
flowchart LR
  V1[v1 exports] --> RAW[v2 raw extract folder]
  RAW --> ETL[v2 ETL]
  ETL --> CUR[v2 curated KPI tables]
  CUR --> BI[Dashboard exports (PNG)]
```
