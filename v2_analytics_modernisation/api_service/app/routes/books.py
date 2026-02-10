from __future__ import annotations
from fastapi import APIRouter
import pandas as pd
from pathlib import Path

router = APIRouter()


@router.get("/")
def list_books(limit: int = 20):
    base = Path(__file__).resolve().parents[3]
    curated = base / "data_output/curated/dim_book.csv"
    if not curated.exists():
        return {"error": "Curated dim_book.csv not found. Run ETL first."}
    df = pd.read_csv(curated).head(limit)
    return {"count": int(df.shape[0]), "items": df.to_dict(orient="records")}
