-- OLTP schema reference (v2)
-- In production, this would be the operational database.
-- In this portfolio, raw CSVs simulate extracts from such a system.

-- Books
-- Members
-- Transactions

-- STAGE LAYER---

CREATE TABLE stg_books (
    batch_id        INT,
    load_dts        DATETIME DEFAULT GETDATE(),

    book_id         VARCHAR(50),
    isbn            VARCHAR(50),
    title           VARCHAR(255),
    author          VARCHAR(255),
    category        VARCHAR(100),
    published_year  VARCHAR(10),
    copies_total    VARCHAR(10),
    copies_available VARCHAR(10)
);



CREATE TABLE stg_members (
    batch_id       INT,
    load_dts       DATETIME DEFAULT GETDATE(),

    member_id      VARCHAR(50),
    member_name    VARCHAR(255),
    membership_type VARCHAR(100),
    join_date      VARCHAR(50),
    status         VARCHAR(50)
);


CREATE TABLE stg_issues (
    batch_id        INT,
    load_dts        DATETIME DEFAULT GETDATE(),

    transaction_id  VARCHAR(50),
    member_id       VARCHAR(50),
    book_id         VARCHAR(50),

    issue_date      VARCHAR(50),
    due_date        VARCHAR(50),
    return_date     VARCHAR(50),

    fine_amount     VARCHAR(50),
    fine_paid       VARCHAR(50)
);


CREATE TABLE stg_fines (
    batch_id        INT,
    load_dts        DATETIME DEFAULT GETDATE(),

    fine_id         VARCHAR(50),
    transaction_id  VARCHAR(50),
    member_id       VARCHAR(50),
    book_id         VARCHAR(50),

    fine_amount     VARCHAR(50),
    fine_paid       VARCHAR(50),
    paid_date       VARCHAR(50)
);



-------------------------------------------------Operational Data------------------------
--------
--Operationa data

IF OBJECT_ID('dbo.books','U') IS NOT NULL DROP TABLE dbo.books;
GO

CREATE TABLE dbo.books (
    book_id           VARCHAR(50)  NOT NULL PRIMARY KEY,  -- matches stg_books.book_id
    isbn              VARCHAR(50)  NULL,
    title             VARCHAR(255) NOT NULL,
    author            VARCHAR(255) NULL,
    category          VARCHAR(100) NULL,
    published_year    INT          NULL,
    copies_total      INT          NULL,
    copies_available  INT          NULL,
    is_active         BIT          NOT NULL DEFAULT 1,
    created_at        DATETIME     NOT NULL DEFAULT GETDATE(),
    updated_at        DATETIME     NOT NULL DEFAULT GETDATE()
);

-- avoid duplicate isbn if you want
CREATE UNIQUE INDEX UX_books_isbn
ON dbo.books(isbn)
WHERE isbn IS NOT NULL;
GO


/* =========================================================
   2) MEMBERS (operational)
   ========================================================= */
IF OBJECT_ID('dbo.members','U') IS NOT NULL DROP TABLE dbo.members;
GO

CREATE TABLE dbo.members (
    member_id        VARCHAR(50)  NOT NULL PRIMARY KEY,   -- matches stg_members.member_id
    member_name      VARCHAR(255) NOT NULL,
    membership_type  VARCHAR(100) NULL,
    join_date        DATE         NULL,
    status           VARCHAR(50)  NOT NULL DEFAULT 'Active',
    is_active        BIT          NOT NULL DEFAULT 1,
    created_at       DATETIME     NOT NULL DEFAULT GETDATE(),
    updated_at       DATETIME     NOT NULL DEFAULT GETDATE()
);
GO


/* =========================================================
   3) ISSUE STATUS 
   ========================================================= */
IF OBJECT_ID('dbo.issue_status_lkp','U') IS NOT NULL DROP TABLE dbo.issue_status_lkp;
GO

CREATE TABLE dbo.issue_status_lkp (
    issue_status_id INT NOT NULL PRIMARY KEY,
    status_name     VARCHAR(50) NOT NULL UNIQUE
);

MERGE dbo.issue_status_lkp AS t
USING (VALUES
  (1, 'Issued'),
  (2, 'Returned'),
  (3, 'Overdue')
) AS s(issue_status_id, status_name)
ON t.issue_status_id = s.issue_status_id
WHEN MATCHED AND t.status_name <> s.status_name THEN
  UPDATE SET status_name = s.status_name
WHEN NOT MATCHED THEN
  INSERT (issue_status_id, status_name) VALUES (s.issue_status_id, s.status_name);
GO


/* =========================================================
   4) ISSUE TRANSACTIONS (operational)
   ========================================================= */
IF OBJECT_ID('dbo.issue_transactions','U') IS NOT NULL DROP TABLE dbo.issue_transactions;
GO

CREATE TABLE dbo.issue_transactions (
    transaction_id   VARCHAR(50) NOT NULL PRIMARY KEY,   -- matches stg_issues.transaction_id

    member_id        VARCHAR(50) NOT NULL,
    book_id          VARCHAR(50) NOT NULL,

    issue_date       DATE        NOT NULL,
    due_date         DATE        NOT NULL,
    return_date      DATE        NULL,

    issue_status_id  INT         NOT NULL DEFAULT 1,      -- Issued by default

    fine_amount      DECIMAL(10,2) NOT NULL DEFAULT 0,
    fine_paid        BIT           NOT NULL DEFAULT 0,

    created_at       DATETIME    NOT NULL DEFAULT GETDATE(),
    updated_at       DATETIME    NOT NULL DEFAULT GETDATE(),

    CONSTRAINT fk_issue_member FOREIGN KEY (member_id)
      REFERENCES dbo.members(member_id),

    CONSTRAINT fk_issue_book FOREIGN KEY (book_id)
      REFERENCES dbo.books(book_id),

    CONSTRAINT fk_issue_status FOREIGN KEY (issue_status_id)
      REFERENCES dbo.issue_status_lkp(issue_status_id),

    CONSTRAINT ck_issue_dates CHECK (due_date >= issue_date),
    CONSTRAINT ck_fine_amount CHECK (fine_amount >= 0)
);



-- Rule: a member cannot have the SAME book currently issued twice 
CREATE UNIQUE INDEX UX_member_active_book
ON dbo.issue_transactions(member_id, book_id)
WHERE return_date IS NULL;
GO


/* =========================================================
   5) FINES / PAYMENTS 
   ========================================================= */
IF OBJECT_ID('dbo.fines','U') IS NOT NULL DROP TABLE dbo.fines;
GO

CREATE TABLE dbo.fines (
    fine_id         VARCHAR(50) NOT NULL PRIMARY KEY,     -- matches stg_fines.fine_id
    transaction_id  VARCHAR(50) NOT NULL,

    member_id       VARCHAR(50) NULL,
    book_id         VARCHAR(50) NULL,

    fine_amount     DECIMAL(10,2) NOT NULL DEFAULT 0,
    fine_paid       BIT           NOT NULL DEFAULT 0,
    paid_date       DATE          NULL,

    created_at      DATETIME      NOT NULL DEFAULT GETDATE(),

    CONSTRAINT fk_fines_tx FOREIGN KEY (transaction_id)
      REFERENCES dbo.issue_transactions(transaction_id),

    CONSTRAINT fk_fines_member FOREIGN KEY (member_id)
      REFERENCES dbo.members(member_id),

    CONSTRAINT fk_fines_book FOREIGN KEY (book_id)
      REFERENCES dbo.books(book_id),

    CONSTRAINT ck_fines_amount CHECK (fine_amount >= 0)
);

CREATE INDEX IX_fines_tx ON dbo.fines(transaction_id);
GO


/* =========================================================
   6) OVERDUE VIEW 
   ========================================================= */
    CREATE OR ALTER VIEW dbo.vw_overdue AS
    SELECT
      it.transaction_id,
      it.member_id,
      it.book_id,
      it.issue_date,
      it.due_date,
      it.return_date,
      CASE
        WHEN it.return_date IS NULL AND it.due_date < CAST(GETDATE() AS date)
          THEN DATEDIFF(day, it.due_date, CAST(GETDATE() AS date))
        WHEN it.return_date IS NOT NULL AND it.return_date > it.due_date
          THEN DATEDIFF(day, it.due_date, it.return_date)
        ELSE 0
      END AS days_overdue,
      CASE
        WHEN (it.return_date IS NULL AND it.due_date < CAST(GETDATE() AS date))
          OR (it.return_date IS NOT NULL AND it.return_date > it.due_date)
        THEN 1 ELSE 0
      END AS overdue_flag
    FROM dbo.issue_transactions it;
    GO


