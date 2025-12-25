from __future__ import annotations

from pathlib import Path
import pandas as pd


def _find_col(cols: list[str], candidates: list[str]) -> str | None:
    lower = {c.lower(): c for c in cols}
    for cand in candidates:
        if cand in lower:
            return lower[cand]
    return None


def read_generic_csv(csv_path: Path) -> pd.DataFrame:
    """
    Generic CSV reader that tries to map common bank CSV headers.
    Requires at least Date, Description, Amount (case-insensitive).
    """
    df = pd.read_csv(csv_path)

    date_col = _find_col(df.columns.tolist(), ["date", "transaction date", "posted date"])
    desc_col = _find_col(df.columns.tolist(), ["description", "transaction description", "details", "name", "merchant"])
    amt_col = _find_col(df.columns.tolist(), ["amount", "transaction amount", "amt"])
    cat_col = _find_col(df.columns.tolist(), ["category", "type"])

    if not date_col or not desc_col or not amt_col:
        raise ValueError(
            "Could not detect required columns. Need at least: Date, Description, Amount.\n"
            f"Found columns: {list(df.columns)}"
        )

    out = pd.DataFrame()
    out["date"] = pd.to_datetime(df[date_col], errors="coerce").dt.strftime("%Y-%m-%d")
    out["description"] = df[desc_col].astype(str)
    out["amount"] = pd.to_numeric(df[amt_col], errors="coerce")

    if cat_col:
        out["category"] = df[cat_col].astype(str)
    else:
        out["category"] = None

    out = out.dropna(subset=["date", "amount"])
    return out
