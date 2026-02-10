CREATE TABLE dim_book (
  book_key SERIAL PRIMARY KEY,
  book_id TEXT UNIQUE NOT NULL,
  isbn TEXT,
  title TEXT NOT NULL,
  author TEXT NOT NULL,
  category TEXT NOT NULL,
  branch TEXT NOT NULL,
  published_year INTEGER,
  copies_total INTEGER,
  price NUMERIC(10,2)
);
