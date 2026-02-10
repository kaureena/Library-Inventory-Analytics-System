# v1 Validation Rules

## Book rules
- `book_id` must be unique
- `copies_total` >= 0
- `copies_available` between 0 and `copies_total`

## Member rules
- `member_id` must be unique
- `status` in {Active, Inactive}

## Issue/Return rules
- Cannot issue a book if `copies_available` is 0
- `due_date` must be after `issue_date`
- `return_date` cannot be before `issue_date`
- Fine is charged only when `return_date` > `due_date`
