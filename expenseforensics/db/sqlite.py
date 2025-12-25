from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


def get_db_path(name: str) -> Path:
    # store DB in project root
    return Path.cwd() / name


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                description TEXT NOT NULL,
                merchant TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT,
                account TEXT NOT NULL
            );
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_txn_date ON transactions(date);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_txn_merchant ON transactions(merchant);")
        conn.commit()


def insert_transactions(db_path: Path, df: pd.DataFrame, account: str) -> int:
    required = {"date", "description", "amount", "merchant"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if "category" not in df.columns:
        df["category"] = None

    df_to_insert = df[["date", "description", "merchant", "amount", "category"]].copy()
    df_to_insert["account"] = account

    rows = df_to_insert.to_records(index=False).tolist()

    with sqlite3.connect(db_path) as conn:
        conn.executemany(
            "INSERT INTO transactions (date, description, merchant, amount, category, account) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            rows,
        )
        conn.commit()

    return len(rows)
