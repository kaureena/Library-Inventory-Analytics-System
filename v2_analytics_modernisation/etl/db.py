import pyodbc
from.Config import SQL_SERVER, SQL_DATABASE,SQL_DRIVER

def get_connection():
    conn_str = (
        f"DRIVER={{{SQL_DRIVER}}};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={SQL_DATABASE};"
        "Trusted_Connection=yes;"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)

def execute_sql(conn, sql: str, params=None):
    params = params or []
    cur = conn.cursor()
    cur.execute(sql, params)
    cur.commit()

def executemany(conn, sql: str, rows: list[tuple]):
    cur = conn.cursor()
    cur.fast_executemany = True
    cur.executemany(sql, rows)
    cur.commit()
