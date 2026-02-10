from ..Config import BATCH_ID
from ..db import get_connection, execute_sql


def transform_staging_to_operational():
    conn = get_connection()
    batch_id = int(BATCH_ID)

    try:
        # ---------------------------------------------------------
        # 0) Reject log (create once if missing)
        # ---------------------------------------------------------
        execute_sql(conn, """
        IF OBJECT_ID('dbo.etl_reject_log', 'U') IS NULL
        BEGIN
          CREATE TABLE dbo.etl_reject_log (
            reject_id INT IDENTITY(1,1) PRIMARY KEY,
            batch_id INT NOT NULL,
            record_key VARCHAR(100) NULL,
            table_name VARCHAR(50) NOT NULL,
            reason VARCHAR(255) NOT NULL,
            created_at DATETIME NOT NULL DEFAULT GETDATE()
          );
          CREATE INDEX IX_etl_reject_log_batch ON dbo.etl_reject_log(batch_id);
        END;
        """)

        # ---------------------------------------------------------
        # 1) Seed lookup table: issue_status_lkp
        # ---------------------------------------------------------
        execute_sql(conn, """
        MERGE dbo.issue_status_lkp AS t
        USING (VALUES
          (1, 'Issued'),
          (2, 'Returned'),
          (3, 'Overdue')
        ) AS s(issue_status_id, status_name)
        ON t.issue_status_id = s.issue_status_id
        WHEN MATCHED AND t.status_name <> s.status_name
          THEN UPDATE SET status_name = s.status_name
        WHEN NOT MATCHED
          THEN INSERT (issue_status_id, status_name)
               VALUES (s.issue_status_id, s.status_name);
        """)

        # ---------------------------------------------------------
        # 2) BOOKS (MERGE) - master data (DEDUP SOURCE to avoid MERGE 8672)
        # ---------------------------------------------------------
        execute_sql(conn, """
        ;WITH src AS (
            SELECT
              book_id,
              NULLIF(LTRIM(RTRIM(isbn)), '') AS isbn,
              NULLIF(LTRIM(RTRIM(title)), '') AS title,
              NULLIF(LTRIM(RTRIM(author)), '') AS author,
              NULLIF(LTRIM(RTRIM(category)), '') AS category,
              TRY_CONVERT(int, NULLIF(LTRIM(RTRIM(published_year)), '')) AS published_year,
              TRY_CONVERT(int, NULLIF(LTRIM(RTRIM(copies_total)), '')) AS copies_total,
              TRY_CONVERT(int, NULLIF(LTRIM(RTRIM(copies_available)), '')) AS copies_available,
              ROW_NUMBER() OVER (
                PARTITION BY book_id
                ORDER BY load_dts DESC
              ) AS rn
            FROM dbo.stg_books
            WHERE batch_id = ?
        ),
        dedup AS (
            SELECT *
            FROM src
            WHERE rn = 1
        )
        MERGE dbo.books AS t
        USING dedup AS s
        ON t.book_id = s.book_id
        WHEN MATCHED THEN
          UPDATE SET
            t.isbn = s.isbn,
            t.title = COALESCE(s.title, t.title),
            t.author = s.author,
            t.category = s.category,
            t.published_year = s.published_year,
            t.copies_total = s.copies_total,
            t.copies_available = s.copies_available,
            t.updated_at = GETDATE()
        WHEN NOT MATCHED THEN
          INSERT (book_id, isbn, title, author, category, published_year, copies_total, copies_available)
          VALUES (s.book_id, s.isbn, COALESCE(s.title,'(unknown)'), s.author, s.category,
                  s.published_year, s.copies_total, s.copies_available);
        """, [batch_id])

        # Log bad books with missing book_id or title
        execute_sql(conn, """
        INSERT INTO dbo.etl_reject_log(batch_id, record_key, table_name, reason)
        SELECT ?, COALESCE(book_id,'(null)'), 'books', 'Missing book_id or title in stg_books'
        FROM dbo.stg_books
        WHERE batch_id = ?
          AND (book_id IS NULL OR LTRIM(RTRIM(book_id)) = '' OR title IS NULL OR LTRIM(RTRIM(title)) = '');
        """, [batch_id, batch_id])

        # ---------------------------------------------------------
        # 3) MEMBERS (MERGE) - master data (DEDUP SOURCE to avoid MERGE 8672)
        # ---------------------------------------------------------
        execute_sql(conn, """
        ;WITH src AS (
            SELECT
              member_id,
              NULLIF(LTRIM(RTRIM(member_name)), '') AS member_name,
              NULLIF(LTRIM(RTRIM(membership_type)), '') AS membership_type,
              TRY_CONVERT(date, NULLIF(LTRIM(RTRIM(join_date)), '')) AS join_date,
              COALESCE(NULLIF(LTRIM(RTRIM(status)), ''), 'Active') AS status,
              ROW_NUMBER() OVER (
                PARTITION BY member_id
                ORDER BY load_dts DESC
              ) AS rn
            FROM dbo.stg_members
            WHERE batch_id = ?
        ),
        dedup AS (
            SELECT *
            FROM src
            WHERE rn = 1
        )
        MERGE dbo.members AS t
        USING dedup AS s
        ON t.member_id = s.member_id
        WHEN MATCHED THEN
          UPDATE SET
            t.member_name = COALESCE(s.member_name, t.member_name),
            t.membership_type = s.membership_type,
            t.join_date = s.join_date,
            t.status = COALESCE(s.status, t.status),
            t.updated_at = GETDATE()
        WHEN NOT MATCHED THEN
          INSERT (member_id, member_name, membership_type, join_date, status)
          VALUES (s.member_id, COALESCE(s.member_name,'(unknown)'),
                  s.membership_type, s.join_date, COALESCE(s.status,'Active'));
        """, [batch_id])

        # Log bad members with missing member_id or member_name
        execute_sql(conn, """
        INSERT INTO dbo.etl_reject_log(batch_id, record_key, table_name, reason)
        SELECT ?, COALESCE(member_id,'(null)'), 'members', 'Missing member_id or member_name in stg_members'
        FROM dbo.stg_members
        WHERE batch_id = ?
          AND (member_id IS NULL OR LTRIM(RTRIM(member_id)) = '' OR member_name IS NULL OR LTRIM(RTRIM(member_name)) = '');
        """, [batch_id, batch_id])

        # ---------------------------------------------------------
        # 4) ISSUE_TRANSACTIONS (APPEND / INSERT ONLY) - history
        #    - Dedups active duplicates (member_id, book_id where return_date is NULL) in-batch
        #    - Skips if an active issue already exists in operational (UX_member_active_book)
        # ---------------------------------------------------------

        execute_sql(conn, """
        INSERT INTO dbo.etl_reject_log(batch_id, record_key, table_name, reason)
        SELECT ?, s.transaction_id, 'issue_transactions', 'Missing FK: member_id or book_id not found in operational master'
        FROM dbo.stg_issues s
        LEFT JOIN dbo.members m ON m.member_id = s.member_id
        LEFT JOIN dbo.books b   ON b.book_id   = s.book_id
        WHERE s.batch_id = ?
          AND (m.member_id IS NULL OR b.book_id IS NULL);
        """, [batch_id, batch_id])

        # Log duplicates within staging batch for active (member_id, book_id)
        execute_sql(conn, """
        ;WITH x AS (
          SELECT
            s.batch_id,
            s.transaction_id,
            s.member_id,
            s.book_id,
            ROW_NUMBER() OVER (
              PARTITION BY s.batch_id, s.member_id, s.book_id
              ORDER BY s.transaction_id
            ) AS rn
          FROM dbo.stg_issues s
          WHERE s.batch_id = ?
            AND (s.return_date IS NULL OR LTRIM(RTRIM(s.return_date)) = '')
        )
        INSERT INTO dbo.etl_reject_log(batch_id, record_key, table_name, reason)
        SELECT ?, transaction_id, 'issue_transactions',
               'Duplicate active issue in stg_issues for same member_id + book_id (keeping first)'
        FROM x
        WHERE rn > 1;
        """, [batch_id, batch_id])

        # Insert valid issues only (dedup in-batch)
        execute_sql(conn, """
        ;WITH src AS (
          SELECT
            s.transaction_id,
            s.member_id,
            s.book_id,
            TRY_CONVERT(date, NULLIF(LTRIM(RTRIM(s.issue_date)), '')) AS issue_date_c,
            TRY_CONVERT(date, NULLIF(LTRIM(RTRIM(s.due_date)), ''))  AS due_date_c,
            TRY_CONVERT(date, NULLIF(LTRIM(RTRIM(s.return_date)), '')) AS return_date_c,
            COALESCE(TRY_CONVERT(decimal(10,2), NULLIF(LTRIM(RTRIM(s.fine_amount)), '')), 0) AS fine_amount_c,
            CASE
              WHEN LOWER(LTRIM(RTRIM(COALESCE(s.fine_paid,'')))) IN ('1','true','yes','y') THEN 1
              ELSE 0
            END AS fine_paid_c,
            ROW_NUMBER() OVER (
              PARTITION BY s.transaction_id
              ORDER BY s.load_dts DESC
            ) AS rn_tx
          FROM dbo.stg_issues s
          WHERE s.batch_id = ?
            AND s.transaction_id IS NOT NULL
            AND LTRIM(RTRIM(s.transaction_id)) <> ''
        ),
        tx_dedup AS (
          SELECT *
          FROM src
          WHERE rn_tx = 1
        ),
        final_dedup AS (
          SELECT
            t.*,
            CASE
              WHEN t.return_date_c IS NULL THEN
                ROW_NUMBER() OVER (PARTITION BY t.member_id, t.book_id ORDER BY t.transaction_id)
              ELSE 1
            END AS rn_active
          FROM tx_dedup t
        )
        INSERT INTO dbo.issue_transactions
        (transaction_id, member_id, book_id, issue_date, due_date, return_date,
         issue_status_id, fine_amount, fine_paid)
        SELECT
          d.transaction_id,
          d.member_id,
          d.book_id,
          d.issue_date_c AS issue_date,
          d.due_date_c   AS due_date,
          d.return_date_c AS return_date,
          CASE
            WHEN d.return_date_c IS NOT NULL THEN 2
            WHEN d.due_date_c < CAST(GETDATE() AS date) THEN 3
            ELSE 1
          END AS issue_status_id,
          d.fine_amount_c AS fine_amount,
          d.fine_paid_c AS fine_paid
        FROM final_dedup d
        JOIN dbo.members m ON m.member_id = d.member_id
        JOIN dbo.books b   ON b.book_id   = d.book_id
        WHERE d.rn_active = 1
          AND d.issue_date_c IS NOT NULL
          AND d.due_date_c IS NOT NULL
          AND NOT EXISTS (
            SELECT 1 FROM dbo.issue_transactions it
            WHERE it.transaction_id = d.transaction_id
          )
          AND NOT EXISTS (
            SELECT 1
            FROM dbo.issue_transactions it2
            WHERE it2.member_id = d.member_id
              AND it2.book_id = d.book_id
              AND it2.return_date IS NULL
              AND d.return_date_c IS NULL
          );
        """, [batch_id])

        # Reject issues with bad dates (issue_date/due_date invalid)
        execute_sql(conn, """
        INSERT INTO dbo.etl_reject_log(batch_id, record_key, table_name, reason)
        SELECT ?, s.transaction_id, 'issue_transactions', 'Invalid issue_date or due_date (cannot TRY_CONVERT to date)'
        FROM dbo.stg_issues s
        WHERE s.batch_id = ?
          AND s.transaction_id IS NOT NULL
          AND LTRIM(RTRIM(s.transaction_id)) <> ''
          AND (
               TRY_CONVERT(date, NULLIF(LTRIM(RTRIM(s.issue_date)), '')) IS NULL
            OR TRY_CONVERT(date, NULLIF(LTRIM(RTRIM(s.due_date)), ''))  IS NULL
          );
        """, [batch_id, batch_id])

        # Log rows skipped because an active issue already exists in operational
        execute_sql(conn, """
        INSERT INTO dbo.etl_reject_log(batch_id, record_key, table_name, reason)
        SELECT ?, s.transaction_id, 'issue_transactions',
               'Active issue already exists in operational for this member_id + book_id'
        FROM dbo.stg_issues s
        WHERE s.batch_id = ?
          AND (s.return_date IS NULL OR LTRIM(RTRIM(s.return_date)) = '')
          AND EXISTS (
              SELECT 1
              FROM dbo.issue_transactions it2
              WHERE it2.member_id = s.member_id
                AND it2.book_id = s.book_id
                AND it2.return_date IS NULL
          );
        """, [batch_id, batch_id])

        # ---------------------------------------------------------
        # 5) FINES (MERGE) - from stg_fines (DEDUP SOURCE)
        # ---------------------------------------------------------
        execute_sql(conn, """
        ;WITH src AS (
          SELECT
            fine_id,
            transaction_id,
            member_id,
            book_id,
            COALESCE(TRY_CONVERT(decimal(10,2), NULLIF(LTRIM(RTRIM(fine_amount)), '')), 0) AS fine_amount,
            CASE
              WHEN LOWER(LTRIM(RTRIM(COALESCE(fine_paid,'')))) IN ('1','true','yes','y') THEN 1
              ELSE 0
            END AS fine_paid,
            TRY_CONVERT(date, NULLIF(LTRIM(RTRIM(paid_date)), '')) AS paid_date,
            ROW_NUMBER() OVER (
              PARTITION BY fine_id
              ORDER BY load_dts DESC
            ) AS rn
          FROM dbo.stg_fines
          WHERE batch_id = ?
        ),
        dedup AS (
          SELECT * FROM src WHERE rn = 1
        )
        MERGE dbo.fines AS t
        USING dedup AS s
        ON t.fine_id = s.fine_id
        WHEN MATCHED THEN
          UPDATE SET
            t.transaction_id = s.transaction_id,
            t.member_id = s.member_id,
            t.book_id = s.book_id,
            t.fine_amount = s.fine_amount,
            t.fine_paid = s.fine_paid,
            t.paid_date = s.paid_date
        WHEN NOT MATCHED THEN
          INSERT (fine_id, transaction_id, member_id, book_id, fine_amount, fine_paid, paid_date)
          VALUES (s.fine_id, s.transaction_id, s.member_id, s.book_id, s.fine_amount, s.fine_paid, s.paid_date);
        """, [batch_id])

        # Reject fines where transaction_id not found in issue_transactions
        execute_sql(conn, """
        INSERT INTO dbo.etl_reject_log(batch_id, record_key, table_name, reason)
        SELECT ?, s.fine_id, 'fines', 'transaction_id not found in issue_transactions'
        FROM dbo.stg_fines s
        LEFT JOIN dbo.issue_transactions it ON it.transaction_id = s.transaction_id
        WHERE s.batch_id = ?
          AND it.transaction_id IS NULL;
        """, [batch_id, batch_id])

        print(f"[OK] Transformed staging → operational for batch_id={batch_id}")

    finally:
        conn.close()
