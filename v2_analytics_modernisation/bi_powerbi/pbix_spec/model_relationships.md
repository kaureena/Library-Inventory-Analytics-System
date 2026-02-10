# Model Relationships (Star Schema)

## Tables
- **dim_book** (book_id)
- **dim_member** (member_id)
- **dim_branch** (branch, branch_id)
- **dim_category** (category, category_id)
- **fact_issue_return** (transaction_id, member_id, book_id, branch, category)
- **fact_fines** (subset of fact_issue_return where fine_amount > 0)

## Relationships
1. dim_book[book_id] 1 → * fact_issue_return[book_id]
2. dim_member[member_id] 1 → * fact_issue_return[member_id]
3. dim_branch[branch] 1 → * fact_issue_return[branch]
4. dim_category[category] 1 → * fact_issue_return[category]

Optional (date dimension):
- Create a calendar table (Date) and relate:
  - Date[Date] 1 → * fact_issue_return[issue_date]
  - Date[Date] 1 → * fact_issue_return[return_date] (inactive relationship)

## Notes
- Keep relationship direction single (dimension → fact)
- Use inactive relationship for alternate date analysis (e.g., return_date)
