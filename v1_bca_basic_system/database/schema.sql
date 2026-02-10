-- SQLite schema (v1 baseline)

CREATE TABLE IF NOT EXISTS books (
  book_id TEXT PRIMARY KEY,
  isbn TEXT,
  title TEXT NOT NULL,
  author TEXT NOT NULL,
  category TEXT NOT NULL,
  published_year INTEGER,
  copies_total INTEGER NOT NULL CHECK (copies_total >= 0),
  copies_available INTEGER NOT NULL CHECK (copies_available >= 0)
);

CREATE TABLE IF NOT EXISTS members (
  member_id TEXT PRIMARY KEY,
  member_name TEXT NOT NULL,
  membership_type TEXT NOT NULL, -- Student/Staff/Public
  join_date TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'Active'
);

CREATE TABLE IF NOT EXISTS transactions (
  transaction_id TEXT PRIMARY KEY,
  member_id TEXT NOT NULL REFERENCES members(member_id),
  book_id TEXT NOT NULL REFERENCES books(book_id),
  issue_date TEXT NOT NULL,
  due_date TEXT NOT NULL,
  return_date TEXT,
  fine_amount REAL NOT NULL DEFAULT 0.0,
  fine_paid INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_tx_member ON transactions(member_id);
CREATE INDEX IF NOT EXISTS idx_tx_book ON transactions(book_id);
