from __future__ import annotations
import pandas as pd

def _normalize_amount_sign(df: pd.DataFrame) -> pd.DataFrame:
    """
    Different banks store spending as positive or negative.
    We'll convert to positive 'spend' for analysis.
    """
    d = df.copy()
    # If most amounts are negative, treat negative as spend.
    if (d["amount"] < 0).mean() > 0.5:
        d["spend"] = d["amount"].abs()
    else:
        d["spend"] = d["amount"].clip(lower=0)
    return d

def detect_monthly_recurring(df: pd.DataFrame, min_occurrences: int = 3) -> pd.DataFrame:
    d = _normalize_amount_sign(df)
    d = d[d["spend"] > 0].copy()

    results = []
    for merchant, g in d.groupby("merchant"):
        g = g.sort_values("date")
        if len(g) < min_occurrences:
            continue

        gaps = g["date"].diff().dt.days.dropna()
        if gaps.empty:
            continue

        monthly_ratio = ((gaps >= 26) & (gaps <= 33)).mean()
        if monthly_ratio >= 0.6:
            results.append({
                "merchant": merchant,
                "count": int(len(g)),
                "typical_amount": float(round(g["spend"].median(), 2)),
                "last_date": g["date"].max().date().isoformat(),
            })

    out = pd.DataFrame(results)
    if out.empty:
        return out
    return out.sort_values(["count", "typical_amount"], ascending=False)

def detect_price_creep(df: pd.DataFrame, min_occurrences: int = 3) -> pd.DataFrame:
    d = _normalize_amount_sign(df)
    d = d[d["spend"] > 0].copy()

    results = []
    for merchant, g in d.groupby("merchant"):
        g = g.sort_values("date")
        if len(g) < min_occurrences:
            continue

        # compare first half median vs second half median
        mid = len(g) // 2
        old = g.iloc[:mid]["spend"].median()
        new = g.iloc[mid:]["spend"].median()

        if pd.notna(old) and pd.notna(new) and new > old * 1.10:  # >10% increase
            results.append({
                "merchant": merchant,
                "old_median": float(round(old, 2)),
                "new_median": float(round(new, 2)),
                "increase_pct": float(round((new - old) / old * 100, 1)),
            })

    out = pd.DataFrame(results)
    if out.empty:
        return out
    return out.sort_values("increase_pct", ascending=False)
