import os
import pandas as pd
from ..Config import V1_EXPORT_DIR, BATCH_ID,BASE_DIR
from ..db import get_connection, executemany,execute_sql
BATCH_ID = int(BATCH_ID)

def load_csv(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing file: {path}")
    return pd.read_csv(path)

def create_staging_tables():
    conn = get_connection()

    sql_path = BASE_DIR / "Staging" / "create_staging_tables.sql"
    print("Using SQL file:", sql_path)

    with open(sql_path, "r", encoding="utf-8") as f:
        sql = f.read()

    execute_sql(conn, sql)
    conn.close()


def as_str(x):
    """Safe convert to string for staging (keeps NULLs as None)."""
    if pd.isna(x):
        return None
    s = str(x).strip()
    return None if s == "" else s


def extract_to_staging():
    """Loads raw export CSVs into staging tables. load_dts is filled by SQL DEFAULT GETDATE()."""
    conn = get_connection()
    try:

        # --- Books ---
        books_path = os.path.join(V1_EXPORT_DIR, "stg_books.csv")  # or "sample_books_export.csv"
        df_books = pd.read_csv(books_path, dtype=str)
        df_books.columns = [c.strip() for c in df_books.columns]

        def as_str(x):
            if pd.isna(x):
                return None
            s = str(x).strip()
            return None if s == "" else s

        # Ensure all expected columns exist (if file missing some, set None)
        expected_cols = [
            "book_id", "isbn", "title", "author", "category",
            "published_year", "copies_total", "copies_available",
            "branch", "acquisition_date", "price"
        ]
        for c in expected_cols:
            if c not in df_books.columns:
                df_books[c] = None

        book_rows = []
        for _, row in df_books.iterrows():
            book_rows.append((
                BATCH_ID,  # batch_id INT
                as_str(row.get("book_id")),
                as_str(row.get("isbn")),
                as_str(row.get("title")),
                as_str(row.get("author")),
                as_str(row.get("category")),
                as_str(row.get("published_year")),
                as_str(row.get("copies_total")),
                as_str(row.get("copies_available")),
                as_str(row.get("branch")),
                as_str(row.get("acquisition_date")),
                as_str(row.get("price")),
            ))

        executemany(
            conn,
            """
            INSERT INTO stg_books
            (batch_id, book_id, isbn, title, author, category, published_year, copies_total, copies_available,
             branch, acquisition_date, price)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            book_rows,
        )

        # -------------------------
        # MEMBERS -> stg_members
        # -------------------------
        members_path = os.path.join(V1_EXPORT_DIR, "stg_members.csv")
        df_members = load_csv(members_path)

        expected_members_cols = ["member_id", "member_name", "membership_type", "join_date", "status"]
        for c in expected_members_cols:
            if c not in df_members.columns:
                df_members[c] = None

        member_rows = []
        for _, row in df_members.iterrows():
            member_rows.append((
                BATCH_ID,
                as_str(row.get("member_id")),
                as_str(row.get("member_name")),
                as_str(row.get("membership_type")),
                as_str(row.get("join_date")),
                as_str(row.get("status")),
            ))

        executemany(conn, """
            INSERT INTO stg_members
                (batch_id,
                 member_id, member_name, membership_type, join_date, status)
            VALUES (?,?,?,?,?,?)
        """, member_rows)

        # -------------------------
        # ISSUES -> stg_issues
        # -------------------------
        issues_path = os.path.join(V1_EXPORT_DIR, "stg_transactions.csv")
        df_issues = load_csv(issues_path)

        expected_issue_cols = [
            "transaction_id", "member_id", "book_id",
            "issue_date", "due_date", "return_date",
            "fine_amount", "fine_paid"
        ]
        for c in expected_issue_cols:
            if c not in df_issues.columns:
                df_issues[c] = None

        issue_rows = []
        for _, row in df_issues.iterrows():
            issue_rows.append((
                BATCH_ID,
                as_str(row.get("transaction_id")),
                as_str(row.get("member_id")),
                as_str(row.get("book_id")),
                as_str(row.get("issue_date")),
                as_str(row.get("due_date")),
                as_str(row.get("return_date")),
                as_str(row.get("fine_amount")),
                as_str(row.get("fine_paid")),
            ))

        executemany(conn, """
            INSERT INTO stg_issues
                (batch_id,
                 transaction_id, member_id, book_id,
                 issue_date, due_date, return_date,
                 fine_amount, fine_paid)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, issue_rows)

        # -------------------------
        # FINES -> stg_fines (optional)
        # -------------------------
        fines_path = os.path.join(V1_EXPORT_DIR, "sample_fines_export.csv")
        if os.path.exists(fines_path):
            df_fines = load_csv(fines_path)

            expected_fine_cols = [
                "fine_id", "transaction_id", "member_id", "book_id",
                "fine_amount", "fine_paid", "paid_date"
            ]
            for c in expected_fine_cols:
                if c not in df_fines.columns:
                    df_fines[c] = None

            fine_rows = []
            for _, row in df_fines.iterrows():
                fine_rows.append((
                    BATCH_ID,
                    as_str(row.get("fine_id")),
                    as_str(row.get("transaction_id")),
                    as_str(row.get("member_id")),
                    as_str(row.get("book_id")),
                    as_str(row.get("fine_amount")),
                    as_str(row.get("fine_paid")),
                    as_str(row.get("paid_date")),
                ))

            executemany(conn, """
                INSERT INTO stg_fines
                    (batch_id,
                     fine_id, transaction_id, member_id, book_id,
                     fine_amount, fine_paid, paid_date)
                VALUES (?,?,?,?,?,?,?,?)
            """, fine_rows)

        print(f"[OK] Extracted exports into staging for batch_id={BATCH_ID}")

    finally:
        conn.close()
