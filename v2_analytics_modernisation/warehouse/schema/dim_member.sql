CREATE TABLE dim_member (
  member_key SERIAL PRIMARY KEY,
  member_id TEXT UNIQUE NOT NULL,
  member_name TEXT NOT NULL,
  membership_type TEXT NOT NULL,
  join_date DATE NOT NULL,
  status TEXT NOT NULL
);
