# Data Model

## OLTP (v1) — core entities

```mermaid
erDiagram
  BOOKS ||--o{ TRANSACTIONS : "book_id"
  MEMBERS ||--o{ TRANSACTIONS : "member_id"

  BOOKS {
    string book_id PK
    string isbn
    string title
    string author
    string category
    int copies_total
    int copies_available
  }

  MEMBERS {
    string member_id PK
    string member_name
    string membership_type
    date join_date
    string status
  }

  TRANSACTIONS {
    string transaction_id PK
    string member_id FK
    string book_id FK
    date issue_date
    date due_date
    date return_date
    float fine_amount
    int fine_paid
  }
```

## Analytics (v2) — curated outputs
- Dimensions:
  - dim_book, dim_member, dim_branch, dim_category
- Facts:
  - fact_issue_return
  - fact_fines
- KPI tables:
  - kpi_daily_issues_returns, kpi_overdue_daily, kpi_fine_weekly, kpi_inventory_health, etc.
