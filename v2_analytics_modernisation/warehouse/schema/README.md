# Warehouse Schema Notes

The warehouse model is described as SQL artefacts for portfolio purposes.

The intended design is a star schema:
- dimensions: date, book, member, branch, category
- facts: issue/return transactions, fines, inventory snapshots

These SQL scripts are not tied to a specific database engine; they can be adapted to PostgreSQL, SQL Server, etc.
