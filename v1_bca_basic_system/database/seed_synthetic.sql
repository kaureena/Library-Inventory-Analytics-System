-- Synthetic seed data (safe for portfolio)

INSERT INTO books(book_id,isbn,title,author,category,published_year,copies_total,copies_available) VALUES
('B001','9780000000001','Intro to SQL','Author_A','IT',2018,5,5),
('B002','9780000000002','Data Analysis Basics','Author_B','Science',2019,3,3),
('B003','9780000000003','History of Gujarat','Author_C','History',2012,4,4);

INSERT INTO members(member_id,member_name,membership_type,join_date,status) VALUES
('M001','Member_001','Student','2025-09-01','Active'),
('M002','Member_002','Staff','2025-06-15','Active'),
('M003','Member_003','Public','2025-01-10','Active');

-- Example transaction (issued and returned late)
INSERT INTO transactions(transaction_id,member_id,book_id,issue_date,due_date,return_date,fine_amount,fine_paid) VALUES
('TX001','M001','B001','2026-01-05','2026-01-12','2026-01-15',3.0,1);
