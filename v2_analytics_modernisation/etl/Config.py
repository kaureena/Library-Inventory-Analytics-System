import os
from pathlib import Path


SQL_SERVER = os.getenv("SQL_SERVER", r"HARIHENIL\SQLEXPRESS01")
SQL_DATABASE = os.getenv("SQL_DATABASE", "LMTS")
SQL_DRIVER = os.getenv("SQL_DRIVER", "ODBC Driver 18 for SQL Server")

# Where your v1 export CSV files sample data
#V1_EXPORT_DIR = os.getenv("V1_EXPORT_DIR", ".../v1_bca_basic_system/export")

BASE_DIR = Path(__file__).resolve().parents[1]
V1_EXPORT_DIR = str((BASE_DIR / "../v1_bca_basic_system/export").resolve())

# Batch id
BATCH_ID = os.getenv("BATCH_ID", "batch_001")


