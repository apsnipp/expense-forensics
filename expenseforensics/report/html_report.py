from pathlib import Path
import pandas as pd
from datetime import datetime

def _df_to_html_table(df: pd.DataFrame) -> str:
    if df is None or df.empty:
        return "<p class='muted'>None found.</p>"
    return df.to_html(index=False, classes="table", border=0)

def build_html_report(
    account: str,
    recurring: pd.DataFrame,
    price_creep: pd.DataFrame,
    trial_to_paid: pd.DataFrame,
) -> str:
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")

    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Expense Forensics Report</title>
  <style>
    :root {{
      --bg: #0b0b12;
      --panel: #121224;
      --text: #eaeaf5;
      --muted: #a6a6c4;
      --border: rgba(255,255,255,0.10);
      --accent: #a855f7;   /* purple */
      --accent2: #7c3aed;  /* deeper purple */
    }}

    body {{
      margin: 0;
      padding: 28px;
      font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Arial, sans-serif;
      background: radial-gradient(1200px 700px at 20% 0%, rgba(168,85,247,0.18), transparent 55%),
                  radial-gradient(900px 600px at 90% 20%, rgba(124,58,237,0.14), transparent 60%),
                  var(--bg);
      color: var(--text);
    }}

    .container {{ max-width: 980px; margin: 0 auto; }}

    h1 {{ margin: 0 0 6px 0; font-size: 28px; }}

    .meta {{
      color: var(--muted);
      margin-bottom: 18px;
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      align-items: center;
    }}

    .pill {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 10px;
      border-radius: 999px;
      border: 1px solid var(--border);
      background: rgba(255,255,255,0.03);
    }}

    .dot {{
      width: 10px; height: 10px; border-radius: 999px;
      background: linear-gradient(135deg, var(--accent), var(--accent2));
      box-shadow: 0 0 0 4px rgba(168,85,247,0.12);
    }}

    code {{
      background: rgba(168,85,247,0.10);
      border: 1px solid rgba(168,85,247,0.25);
      color: var(--text);
      padding: 2px 8px;
      border-radius: 10px;
    }}

    .card {{
      border: 1px solid var(--border);
      background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
      border-radius: 16px;
      padding: 16px;
      margin: 14px 0;
      box-shadow: 0 10px 30px rgba(0,0,0,0.35);
    }}

    .card h2 {{ margin: 0; font-size: 18px; display: flex; align-items: center; gap: 10px; }}

    .badge {{
      font-size: 12px;
      padding: 4px 10px;
      border-radius: 999px;
      border: 1px solid rgba(168,85,247,0.30);
      background: rgba(168,85,247,0.12);
      color: var(--text);
    }}

    .muted {{ color: var(--muted); margin-top: 10px; }}

    .table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 12px;
      overflow: hidden;
      border-radius: 12px;
    }}

    .table th, .table td {{
      padding: 12px 10px;
      border-bottom: 1px solid rgba(255,255,255,0.08);
      text-align: left;
      vertical-align: top;
    }}

    .table th {{
      background: rgba(168,85,247,0.10);
      border-bottom: 1px solid rgba(168,85,247,0.20);
      color: var(--text);
      font-weight: 700;
    }}

    .table tr:nth-child(even) td {{ background: rgba(255,255,255,0.02); }}
    .table tr:hover td {{ background: rgba(168,85,247,0.08); }}
  </style>
</head>

<body>
  <div class="container">
    <h1>Expense Forensics Report</h1>
    <div class="meta">
      <span class="pill"><span class="dot"></span> Account: <code>{account}</code></span>
      <span class="pill">Generated: {generated}</span>
    </div>

    <div class="card">
      <h2>Monthly recurring candidates <span class="badge">Subscriptions</span></h2>
      {_df_to_html_table(recurring)}
    </div>

    <div class="card">
      <h2>Price creep candidates <span class="badge">Increases</span></h2>
      {_df_to_html_table(price_creep)}
    </div>

    <div class="card">
      <h2>Trial → paid candidates <span class="badge">Conversions</span></h2>
      {_df_to_html_table(trial_to_paid)}
    </div>

    <div class="card">
      <h2>How to reproduce <span class="badge">CLI</span></h2>
      <p class="muted">Run: <code>python3 -m expenseforensics.cli analyze --account "{account}"</code></p>
    </div>
  </div>
</body>
</html>
"""
