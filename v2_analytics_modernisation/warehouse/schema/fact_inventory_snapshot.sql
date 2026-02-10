CREATE TABLE fact_inventory_snapshot (
  snapshot_key SERIAL PRIMARY KEY,
  snapshot_date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
  book_key INTEGER NOT NULL REFERENCES dim_book(book_key),
  branch_key INTEGER REFERENCES dim_branch(branch_key),
  copies_total INTEGER NOT NULL,
  on_loan INTEGER NOT NULL,
  est_available INTEGER NOT NULL,
  stockout_flag INTEGER NOT NULL
);
