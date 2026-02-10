CREATE TABLE dim_branch (
  branch_key SERIAL PRIMARY KEY,
  branch_name TEXT UNIQUE NOT NULL
);
