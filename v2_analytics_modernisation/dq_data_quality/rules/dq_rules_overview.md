## DQ Rules Overview

1. **Schema completeness**
   - required columns exist across books/members/transactions

2. **Identity and uniqueness**
   - book_id, member_id, transaction_id must be unique

3. **Referential integrity**
   - all transactions reference valid members and books

4. **Date logic**
   - due_date after issue_date
   - return_date cannot precede issue_date

5. **Fine logic**
   - fine only when overdue
   - fine matches overdue days × policy

6. **Inventory sanity**
   - copies_available between 0 and copies_total

7. **Monitoring completeness**
   - refresh snapshots and export counts present
