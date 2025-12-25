from __future__ import annotations

import pandas as pd

STRIP_WORDS = ["TRIAL", "PENDING", "VERIFY", "VERIFICATION"]

def _normalize_amount_sign(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    if (d["amount"] < 0).mean() > 0.5:
        d["spend"] = d["amount"].abs()
    else:
        d["spend"] = d["amount"].clip(lower=0)
    return d

def _merchant_key(merchant: str) -> str:
    s = str(merchant).upper()
    for w in STRIP_WORDS:
        s = s.replace(w, " ")
    s = " ".join(s.split())
    return s.title() if s else "Unknown"

def detect_trial_to_paid(
    df: pd.DataFrame,
    trial_max: float = 2.00,
    lookahead_days_min: int = 3,
    lookahead_days_max: int = 30,
    paid_min: float = 8.00,
) -> pd.DataFrame:
    """
    Detect: small charge ($0-$2) -> bigger charge ($8+) within 3-30 days.
    Uses a merchant_key that strips words like TRIAL so:
      "Disney Plus Trial" and "Disney Plus" match.
    """
    d = _normalize_amount_sign(df)
    d = d[d["spend"] > 0].copy()
    if d.empty:
        return pd.DataFrame()

    d = d.sort_values("date").copy()
    d["mkey"] = d["merchant"].apply(_merchant_key)

    results = []

    for mkey, g in d.groupby("mkey"):
        g = g.sort_values("date").reset_index(drop=True)

        trials = g[g["spend"] <= trial_max]
        paid = g[g["spend"] >= paid_min]
        if trials.empty or paid.empty:
            continue

        for _, t in trials.iterrows():
            window_start = t["date"] + pd.Timedelta(days=lookahead_days_min)
            window_end = t["date"] + pd.Timedelta(days=lookahead_days_max)

            cand = paid[(paid["date"] >= window_start) & (paid["date"] <= window_end)]
            if cand.empty:
                continue

            first_paid = cand.iloc[0]
            results.append(
                {
                    "merchant": mkey,
                    "trial_date": t["date"].date().isoformat(),
                    "trial_amount": float(round(t["spend"], 2)),
                    "paid_date": first_paid["date"].date().isoformat(),
                    "paid_amount": float(round(first_paid["spend"], 2)),
                    "days_between": int((first_paid["date"] - t["date"]).days),
                }
            )

    out = pd.DataFrame(results)
    if out.empty:
        return out
    return out.sort_values(["paid_amount", "days_between"], ascending=[False, True])
