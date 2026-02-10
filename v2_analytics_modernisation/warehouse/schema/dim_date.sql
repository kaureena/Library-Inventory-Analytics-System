-- dim_date (generic SQL)
CREATE TABLE dim_date (
  date_key INTEGER PRIMARY KEY,          -- YYYYMMDD
  date_value DATE NOT NULL,
  day_of_week INTEGER,
  month INTEGER,
  quarter INTEGER,
  year INTEGER
);
