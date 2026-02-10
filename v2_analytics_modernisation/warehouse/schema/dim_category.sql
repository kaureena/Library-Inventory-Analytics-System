CREATE TABLE dim_category (
  category_key SERIAL PRIMARY KEY,
  category_name TEXT UNIQUE NOT NULL
);
