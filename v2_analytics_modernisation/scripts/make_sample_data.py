"""Generate synthetic Library raw data (portfolio-safe).

Writes:
- data/raw/books_raw.csv
- data/raw/members_raw.csv
- data/raw/transactions_raw.csv
- data/reference/category_master.csv
- data/reference/branch_master.csv

The generator is deterministic via a fixed random seed.
"""

from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

CATEGORIES = [
    "IT",
    "Science",
    "History",
    "Literature",
    "Maths",
    "Business",
    "Arts",
    "Kids",
]

BRANCHES = ["Central", "North", "South", "East", "West"]


def _isbn13(rng: np.random.Generator, n: int) -> list[str]:
    # simple synthetic ISBN-like numbers (not real)
    base = rng.integers(10**11, 10**12, size=n, dtype=np.int64)
    return [f"978{b:012d}"[:13] for b in base]


def generate(
    seed: int = 42, n_books: int = 500, n_members: int = 220, n_tx: int = 12000
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)

    # Books
    isbn = _isbn13(rng, n_books)
    books = pd.DataFrame(
        {
            "book_id": [f"B{i:04d}" for i in range(1, n_books + 1)],
            "isbn": isbn,
            "title": [f"Book Title {i:04d}" for i in range(1, n_books + 1)],
            "author": [f"Author_{rng.integers(1, 120):03d}" for _ in range(n_books)],
            "category": rng.choice(
                CATEGORIES,
                size=n_books,
                p=[0.18, 0.16, 0.10, 0.14, 0.12, 0.12, 0.10, 0.08],
            ),
            "branch": rng.choice(
                BRANCHES, size=n_books, p=[0.40, 0.15, 0.15, 0.15, 0.15]
            ),
            "published_year": rng.integers(1990, 2025, size=n_books),
            "copies_total": rng.integers(1, 11, size=n_books),
        }
    )
    books["copies_available"] = books["copies_total"]
    books["acquisition_date"] = pd.to_datetime("2022-01-01") + pd.to_timedelta(
        rng.integers(0, 1200, size=n_books), unit="D"
    )
    books["price"] = np.round(rng.uniform(150, 900, size=n_books), 2)

    # Members
    members = pd.DataFrame(
        {
            "member_id": [f"M{i:04d}" for i in range(1, n_members + 1)],
            "member_name": [f"Member_{i:04d}" for i in range(1, n_members + 1)],
            "membership_type": rng.choice(
                ["Student", "Staff", "Public"], size=n_members, p=[0.6, 0.2, 0.2]
            ),
            "join_date": pd.to_datetime("2024-01-01")
            + pd.to_timedelta(rng.integers(0, 760, size=n_members), unit="D"),
            "status": rng.choice(
                ["Active", "Inactive"], size=n_members, p=[0.93, 0.07]
            ),
        }
    )

    # Transactions
    start = pd.to_datetime("2025-08-01")
    end = pd.to_datetime("2026-01-31")
    days = int((end - start).days)

    book_ids = books["book_id"].tolist()
    member_ids = members["member_id"].tolist()

    issue_dates = start + pd.to_timedelta(
        rng.integers(0, days + 1, size=n_tx), unit="D"
    )
    # loan length depends on member type
    member_type_map = members.set_index("member_id")["membership_type"].to_dict()
    m_for_tx = rng.choice(member_ids, size=n_tx, replace=True)
    loan_days = np.array(
        [14 if member_type_map.get(mid) == "Student" else 21 for mid in m_for_tx]
    )
    due_dates = issue_dates + pd.to_timedelta(loan_days, unit="D")

    # return behaviour
    returned = rng.random(size=n_tx) < 0.92
    return_lag = rng.integers(1, 35, size=n_tx)
    return_dates = issue_dates + pd.to_timedelta(return_lag, unit="D")
    return_dates = pd.Series(return_dates)
    return_dates[~returned] = pd.NaT

    # compute fine (simple)
    fine_per_day = 1.0
    days_overdue = ((return_dates - due_dates).dt.days).fillna(0).astype(int)
    days_overdue = days_overdue.clip(lower=0)
    fine_amount = np.round(days_overdue * fine_per_day, 2)

    fine_paid = (fine_amount > 0) & (rng.random(size=n_tx) < 0.7)
    fine_paid = fine_paid.astype(int)

    # choose books; bias towards certain categories
    b_for_tx = rng.choice(book_ids, size=n_tx, replace=True)

    tx = pd.DataFrame(
        {
            "transaction_id": [f"TX{i:06d}" for i in range(1, n_tx + 1)],
            "member_id": m_for_tx,
            "book_id": b_for_tx,
            "issue_date": issue_dates,
            "due_date": due_dates,
            "return_date": return_dates,
            "fine_amount": fine_amount,
            "fine_paid": fine_paid,
        }
    )
    # add branch on tx (use book branch)
    branch_map = books.set_index("book_id")["branch"].to_dict()
    tx["branch"] = tx["book_id"].map(branch_map)

    # Inject a couple of controlled DQ warnings (not catastrophic)
    # 1 row: due_date equals issue_date (should be WARN)
    tx.loc[0, "due_date"] = tx.loc[0, "issue_date"]
    # 1 row: fine_amount >0 but not overdue (should be WARN)
    tx.loc[1, "fine_amount"] = 5.0
    tx.loc[1, "fine_paid"] = 0

    return books, members, tx


def main() -> None:
    base = Path(__file__).resolve().parents[1]  # v2_analytics_modernisation

    raw_dir = base / "data/raw"
    ref_dir = base / "data/reference"
    raw_dir.mkdir(parents=True, exist_ok=True)
    ref_dir.mkdir(parents=True, exist_ok=True)

    books, members, tx = generate()

    books.to_csv(raw_dir / "books_raw.csv", index=False)
    members.to_csv(raw_dir / "members_raw.csv", index=False)
    tx.to_csv(raw_dir / "transactions_raw.csv", index=False)

    pd.DataFrame({"category": CATEGORIES}).to_csv(
        ref_dir / "category_master.csv", index=False
    )
    pd.DataFrame({"branch": BRANCHES}).to_csv(
        ref_dir / "branch_master.csv", index=False
    )

    print(f"Wrote: {raw_dir/'books_raw.csv'} ({len(books):,} rows)")
    print(f"Wrote: {raw_dir/'members_raw.csv'} ({len(members):,} rows)")
    print(f"Wrote: {raw_dir/'transactions_raw.csv'} ({len(tx):,} rows)")


if __name__ == "__main__":
    main()
