CREATE TABLE fact_fines (
  fine_key SERIAL PRIMARY KEY,
  transaction_id TEXT NOT NULL,
  member_key INTEGER NOT NULL REFERENCES dim_member(member_key),
  book_key INTEGER NOT NULL REFERENCES dim_book(book_key),
  branch_key INTEGER REFERENCES dim_branch(branch_key),
  return_date_key INTEGER REFERENCES dim_date(date_key),
  fine_amount NUMERIC(10,2) NOT NULL,
  fine_paid INTEGER NOT NULL
);
