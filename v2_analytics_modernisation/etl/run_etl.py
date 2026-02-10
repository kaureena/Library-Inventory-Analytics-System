from .db import get_connection
from .extract.extract import extract_to_staging,create_staging_tables
from .transform .transform import transform_staging_to_operational
from .load.load import load_operational_to_warehouse
from .load.export_curated import export_curated

def main():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT SYSTEM_USER, @@SERVERNAME")
    print(cur.fetchone())
    cur.execute("SELECT DB_NAME()")
    print("Connected DB:", cur.fetchone()[0])
    conn.close()
    extract_to_staging()
    #create_staging_tables()
    transform_staging_to_operational()
    load_operational_to_warehouse()
    export_curated()

if __name__ == "__main__":
    main()

