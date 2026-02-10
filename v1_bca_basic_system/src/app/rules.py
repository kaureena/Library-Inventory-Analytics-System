"""Business rules for v1 (used by unit tests)."""

from __future__ import annotations
from datetime import date


def due_after_issue(issue_date: date, due_date: date) -> bool:
    return due_date > issue_date


def fine_amount(due_date: date, return_date: date, fine_per_day: float = 1.0) -> float:
    if return_date <= due_date:
        return 0.0
    days = (return_date - due_date).days
    return float(days) * fine_per_day
