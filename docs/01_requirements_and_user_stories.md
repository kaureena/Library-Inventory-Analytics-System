# Requirements and User Stories

## Functional requirements (v1)

### Inventory
1. Add/edit books with validation:
   - copies_total >= 0
   - copies_available between 0 and copies_total
2. Search/filter books by title/author/category/branch
3. Identify stockouts (available == 0)

### Members
1. Add/edit members
2. Membership types: Student, Staff, Public
3. Member status: Active/Inactive

### Issue/Return
1. Issue a book:
   - member must be Active
   - book must have copies_available > 0
   - due_date must be after issue_date
2. Return a book:
   - return_date cannot be before issue_date
   - fine charged only when return_date > due_date
3. Fine rules:
   - fine_per_day policy (default: 1.0/day)
   - fine_paid status tracked

### Exports
1. Export books, members, transactions to CSV
2. Export history is logged (portfolio evidence)

## Analytics requirements (v2)

1. Raw extracts stored as CSV
2. ETL produces:
   - staged tables
   - curated dimensions and facts
   - KPI tables for dashboards
3. DQ gate enforces:
   - schema completeness
   - uniqueness
   - referential integrity
   - date logic
   - fine logic
4. Dashboard exports (PNG) include:
   - operational volume
   - overdue/fine analysis
   - inventory health
   - monitoring (run register + refresh health)

## User stories (examples)

### US-01 Issue a book (Staff)
**As a** staff member  
**I want** to issue a book to a member  
**So that** the borrowing is recorded and stock is updated

Acceptance criteria:
- member is Active
- book is available
- due_date > issue_date

### US-02 Return a book and calculate fine (Staff)
Acceptance criteria:
- if return_date <= due_date then fine = 0
- if return_date > due_date then fine = (days overdue × policy)

### US-03 Monitor pipeline health (Analyst)
Acceptance criteria:
- refresh snapshot exists
- dq_status != FAIL
- expected exports exist
