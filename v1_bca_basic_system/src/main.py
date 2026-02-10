"""v1 baseline: minimal CLI-like demo.

This is not meant to be production-ready.
It exists to show:
- baseline CRUD thinking
- business rules (issue/return/fines)
- ability to export evidence CSVs
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
import csv

DB_PATH = Path(__file__).resolve().parents[1] / "database" / "library_v1.db"


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    schema_path = Path(__file__).resolve().parents[1] / "database" / "schema.sql"
    seed_path = Path(__file__).resolve().parents[1] / "database" / "seed_synthetic.sql"

    conn = connect()
    with conn:
        conn.executescript(schema_path.read_text(encoding="utf-8"))
        conn.executescript(seed_path.read_text(encoding="utf-8"))
    conn.close()


def export_table(table: str, out_path: Path) -> None:
    conn = connect()
    rows = conn.execute(f"SELECT * FROM {table}").fetchall()
    if not rows:
        return
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(rows[0].keys())
        for r in rows:
            w.writerow([r[k] for k in r.keys()])
    conn.close()


def main() -> None:
    init_db()

    base = Path(__file__).resolve().parents[1]
    export_dir = base / "export"

    export_table("books", export_dir / "sample_books_export.csv")
    export_table("members", export_dir / "sample_members_export.csv")
    export_table("transactions", export_dir / "sample_issues_export.csv")

    print("v1 demo complete:")
    print(f"- DB: {DB_PATH}")
    print(f"- Exports: {export_dir}")


if __name__ == "__main__":
    main()
