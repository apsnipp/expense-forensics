from __future__ import annotations

import re
import pandas as pd

NOISE = [
    "POS", "PURCHASE", "DEBIT", "CREDIT", "ONLINE", "PAYMENT", "WITHDRAWAL",
    "ACH", "CHECKCARD", "CHECK CARD", "CARD", "REF", "ID", "AUTH"
]

def normalize_merchant(desc: str) -> str:
    s = str(desc).upper()

    # Remove common noise words
    for w in NOISE:
        s = re.sub(rf"\b{re.escape(w)}\b", " ", s)

    # Remove tokens like *1234 or #1234 and all digits
    s = re.sub(r"[\*\#]\s*\d+", " ", s)
    s = re.sub(r"\d+", " ", s)

    # Keep letters, spaces, and &
    s = re.sub(r"[^A-Z& ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()

    if len(s) > 40:
        s = s[:40].strip()

    return s.title() if s else "Unknown"

def add_merchant_column(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["merchant"] = out["description"].apply(normalize_merchant)
    return out
