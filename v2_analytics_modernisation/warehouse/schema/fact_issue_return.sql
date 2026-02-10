CREATE TABLE fact_issue_return (
  tx_key SERIAL PRIMARY KEY,
  transaction_id TEXT UNIQUE NOT NULL,
  member_key INTEGER NOT NULL REFERENCES dim_member(member_key),
  book_key INTEGER NOT NULL REFERENCES dim_book(book_key),
  branch_key INTEGER REFERENCES dim_branch(branch_key),
  issue_date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
  due_date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
  return_date_key INTEGER REFERENCES dim_date(date_key),
  returned_flag INTEGER NOT NULL,
  overdue_flag INTEGER NOT NULL,
  days_on_loan INTEGER,
  days_overdue INTEGER,
  fine_amount NUMERIC(10,2),
  fine_paid INTEGER
);
