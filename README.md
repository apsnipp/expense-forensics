# Expense Forensics

A Python CLI tool that imports bank transaction CSVs into SQLite and flags “money leaks” like:

- **Monthly recurring charges** (subscriptions)
- **Price creep** (same merchant getting more expensive over time)
- **Trial → Paid conversions** (small trial charge followed by a bigger charge within 3–30 days)

## Features

- Import generic CSVs into a local SQLite database
- Detect recurring subscriptions
- Detect price creep over time
- Detect trial → paid conversions
- Generate a **black + purple HTML report**

## Quickstart (Mac)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install typer pandas rapidfuzz rich
