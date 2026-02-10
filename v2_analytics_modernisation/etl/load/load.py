from ..db import get_connection, execute_sql


def load_operational_to_warehouse():
    """
    Loads operational (curated) tables into warehouse star schema.

    Operational tables expected:
      - dbo.books
      - dbo.members
      - dbo.issue_transactions
      - dbo.fines

    Warehouse tables expected:
      - dbo.dim_category
      - dbo.dim_member
      - dbo.dim_book
      - dbo.dim_date
      - dbo.fact_issue_return
      - dbo.fact_fines
      - dbo.fact_inventory_snapshot
    """

    conn = get_connection()

    try:
        # ============================
        # 1) DIM_DATE (generate)
        # ============================
        execute_sql(conn, """
        DECLARE @target_start DATE = '2010-01-01';
        DECLARE @target_end   DATE = '2035-12-31';

        ;WITH n AS (
            SELECT TOP (DATEDIFF(DAY, @target_start, @target_end) + 1)
                ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) - 1 AS i
            FROM sys.all_objects a
            CROSS JOIN sys.all_objects b
        ),
        d AS (
            SELECT DATEADD(DAY, i, @target_start) AS dt
            FROM n
        )
        INSERT INTO dbo.dim_date
            (date_key, date_value, day_of_week, [month], [quarter], [year])
        SELECT
            CONVERT(INT, FORMAT(dt,'yyyyMMdd')) AS date_key,
            dt AS date_value,
            DATEPART(WEEKDAY, dt) AS day_of_week,
            MONTH(dt) AS [month],
            DATEPART(QUARTER, dt) AS [quarter],
            YEAR(dt) AS [year]
        FROM d
        WHERE NOT EXISTS (
            SELECT 1 FROM dbo.dim_date dd
            WHERE dd.date_key = CONVERT(INT, FORMAT(dt,'yyyyMMdd'))
        );
        """)

        # ============================
        # 2) DIM_CATEGORY (MERGE)
        # ============================
        execute_sql(conn, """
        MERGE dbo.dim_category AS t
        USING (
            SELECT DISTINCT NULLIF(LTRIM(RTRIM(category)), '') AS category_name
            FROM dbo.books
        ) AS s
        ON t.category_name = s.category_name
        WHEN NOT MATCHED AND s.category_name IS NOT NULL THEN
            INSERT (category_name) VALUES (s.category_name);
        """)

        # ============================
        # 3) DIM_MEMBER (MERGE)
        # ============================
        execute_sql(conn, """
        MERGE dbo.dim_member AS t
        USING (
            SELECT
                m.member_id,
                m.member_name,
                m.membership_type,
                m.join_date,
                m.status
            FROM dbo.members m
        ) AS s
        ON t.member_id = s.member_id
        WHEN MATCHED THEN
            UPDATE SET
                t.member_name = s.member_name,
                t.membership_type = s.membership_type,
                t.join_date = s.join_date,
                t.status = s.status
        WHEN NOT MATCHED THEN
            INSERT (member_id, member_name, membership_type, join_date, status)
            VALUES (s.member_id, s.member_name, s.membership_type, s.join_date, s.status);
        """)

        # ============================
        # 4) DIM_BOOK (MERGE)
        #   - category_key lookup from dim_category
        #   - branch_key left NULL (you don’t have branch in operational)
        # ============================
        execute_sql(conn, """
        MERGE dbo.dim_book AS t
        USING (
            SELECT
                b.book_id,
                b.isbn,
                b.title,
                b.author,
                b.published_year,
                b.copies_total,
                b.category,
                dc.category_key
            FROM dbo.books b
            LEFT JOIN dbo.dim_category dc
              ON dc.category_name = NULLIF(LTRIM(RTRIM(b.category)), '')
        ) AS s
        ON t.book_id = s.book_id
        WHEN MATCHED THEN
            UPDATE SET
                t.isbn = s.isbn,
                t.title = s.title,
                t.author = s.author,
                t.published_year = s.published_year,
                t.copies_total = s.copies_total,
                t.category_key = s.category_key
        WHEN NOT MATCHED THEN
            INSERT (book_id, isbn, title, author, category_key, branch_key, published_year, copies_total, price)
            VALUES (s.book_id, s.isbn, s.title, s.author, s.category_key, NULL, s.published_year, s.copies_total, NULL);
        """)

        # ============================
        # 5) FACT_ISSUE_RETURN (APPEND)
        # ============================
        execute_sql(conn, """
        INSERT INTO dbo.fact_issue_return
          (transaction_id,
           member_key, book_key, branch_key,
           issue_date_key, due_date_key, return_date_key,
           returned_flag, overdue_flag,
           days_on_loan, days_overdue,
           fine_amount, fine_paid)
        SELECT
          it.transaction_id,

          dm.member_key,
          db.book_key,
          NULL AS branch_key,

          CONVERT(int, FORMAT(it.issue_date, 'yyyyMMdd')) AS issue_date_key,
          CONVERT(int, FORMAT(it.due_date, 'yyyyMMdd')) AS due_date_key,
          CASE
            WHEN it.return_date IS NULL THEN NULL
            ELSE CONVERT(int, FORMAT(it.return_date, 'yyyyMMdd'))
          END AS return_date_key,

          CASE WHEN it.return_date IS NULL THEN 0 ELSE 1 END AS returned_flag,

          CASE
            WHEN (it.return_date IS NULL AND it.due_date < CAST(GETDATE() AS date))
              OR (it.return_date IS NOT NULL AND it.return_date > it.due_date)
            THEN 1 ELSE 0
          END AS overdue_flag,

          CASE
            WHEN it.return_date IS NULL THEN NULL
            ELSE DATEDIFF(day, it.issue_date, it.return_date)
          END AS days_on_loan,

          CASE
            WHEN it.return_date IS NULL AND it.due_date < CAST(GETDATE() AS date)
              THEN DATEDIFF(day, it.due_date, CAST(GETDATE() AS date))
            WHEN it.return_date IS NOT NULL AND it.return_date > it.due_date
              THEN DATEDIFF(day, it.due_date, it.return_date)
            ELSE 0
          END AS days_overdue,

          it.fine_amount,
          it.fine_paid

        FROM dbo.issue_transactions it
        JOIN dbo.dim_member dm ON dm.member_id = it.member_id
        JOIN dbo.dim_book   db ON db.book_id   = it.book_id
        WHERE NOT EXISTS (
            SELECT 1 FROM dbo.fact_issue_return f
            WHERE f.transaction_id = it.transaction_id
        );
        """)

        # ============================
        # 6) FACT_FINES (APPEND)
        #    Uses dbo.fines operational
        # ============================
        execute_sql(conn, """
        INSERT INTO dbo.fact_fines
          (transaction_id,
           member_key, book_key, branch_key,
           return_date_key,
           fine_amount, fine_paid)
        SELECT
          f.transaction_id,
          dm.member_key,
          db.book_key,
          NULL AS branch_key,
          CASE
            WHEN it.return_date IS NULL THEN NULL
            ELSE CONVERT(int, FORMAT(it.return_date, 'yyyyMMdd'))
          END AS return_date_key,
          f.fine_amount,
          f.fine_paid
        FROM dbo.fines f
        JOIN dbo.issue_transactions it ON it.transaction_id = f.transaction_id
        JOIN dbo.dim_member dm ON dm.member_id = it.member_id
        JOIN dbo.dim_book   db ON db.book_id   = it.book_id
        WHERE NOT EXISTS (
            SELECT 1 FROM dbo.fact_fines ff
            WHERE ff.transaction_id = f.transaction_id
              AND ff.fine_amount = f.fine_amount
              AND ff.fine_paid = f.fine_paid
        );
        """)

        # ============================
        # 7) FACT_INVENTORY_SNAPSHOT (daily snapshot)
        #    Simple version using books.copies_total/available
        # ============================
        execute_sql(conn, """
        DECLARE @today_key INT = CONVERT(int, FORMAT(CAST(GETDATE() AS date),'yyyyMMdd'));

        INSERT INTO dbo.fact_inventory_snapshot
          (snapshot_date_key, book_key, branch_key,
           copies_total, on_loan, est_available, stockout_flag)
        SELECT
          @today_key,
          db.book_key,
          NULL AS branch_key,
          COALESCE(b.copies_total, 0) AS copies_total,
          CASE
            WHEN b.copies_total IS NULL OR b.copies_available IS NULL THEN 0
            WHEN b.copies_total - b.copies_available < 0 THEN 0
            ELSE b.copies_total - b.copies_available
          END AS on_loan,
          COALESCE(b.copies_available, 0) AS est_available,
          CASE WHEN COALESCE(b.copies_available, 0) <= 0 THEN 1 ELSE 0 END AS stockout_flag
        FROM dbo.books b
        JOIN dbo.dim_book db ON db.book_id = b.book_id
        WHERE NOT EXISTS (
            SELECT 1 FROM dbo.fact_inventory_snapshot s
            WHERE s.snapshot_date_key = @today_key
              AND s.book_key = db.book_key
              AND (s.branch_key IS NULL)
        );
        """)

        print("[OK] Loaded operational → warehouse (dims + facts)")

    finally:
        conn.close()
