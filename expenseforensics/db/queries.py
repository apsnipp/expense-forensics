from __future__ import annotations

import sqlite3
from pathlib import Path
import pandas as pd

def load_transactions(db_path: Path, account: str | None = None) -> pd.DataFrame:
    with sqlite3.connect(db_path) as conn:
        if account:
            df = pd.read_sql_query(
                "SELECT date, description, merchant, amount, category, account FROM transactions WHERE account = ?",
                conn,
                params=(account,),
            )
        else:
            df = pd.read_sql_query(
                "SELECT date, description, merchant, amount, category, account FROM transactions",
                conn,
            )

    df["date"] = pd.to_datetime(df["date"])
    return df
