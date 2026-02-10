from __future__ import annotations

from fastapi import FastAPI
from .routes import books, members, issues

app = FastAPI(title="Library API (Portfolio)")

app.include_router(books.router, prefix="/books", tags=["books"])
app.include_router(members.router, prefix="/members", tags=["members"])
app.include_router(issues.router, prefix="/issues", tags=["issues"])


@app.get("/health")
def health():
    return {"status": "ok"}
