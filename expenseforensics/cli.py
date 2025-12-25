import typer
from rich import print
from pathlib import Path

from expenseforensics.db.sqlite import init_db, insert_transactions, get_db_path
from expenseforensics.ingest.csv_ingest import read_generic_csv
from expenseforensics.clean.merchant import add_merchant_column

from expenseforensics.db.queries import load_transactions
from expenseforensics.detect.recurring import detect_monthly_recurring, detect_price_creep
from expenseforensics.detect.trial_to_paid import detect_trial_to_paid
from expenseforensics.report.html_report import build_html_report

app = typer.Typer(help="Expense Forensics: import transactions, detect leaks, generate reports.")


@app.command()
def init(db: str = typer.Option("expenseforensics.sqlite", help="SQLite DB file name")):
    """Initialize the local SQLite database."""
    db_path = get_db_path(db)
    init_db(db_path)
    print(f"[green]Initialized DB:[/green] {db_path}")


@app.command("import-csv")
def import_csv(
    csv_path: Path = typer.Argument(..., exists=True, readable=True),
    account: str = typer.Option("default", help="Account label for this import"),
    db: str = typer.Option("expenseforensics.sqlite", help="SQLite DB file name"),
):
    """Import a bank CSV into the database (generic first; add bank-specific later)."""
    db_path = get_db_path(db)
    init_db(db_path)

    df = read_generic_csv(csv_path)
    df = add_merchant_column(df)
    n = insert_transactions(db_path, df, account=account)

    print(f"[green]Imported[/green] {n} transactions from {csv_path.name} into {db_path}")


@app.command()
def analyze(
    db: str = typer.Option("expenseforensics.sqlite", help="SQLite DB file name"),
    account: str = typer.Option(None, help="Analyze a single account label"),
):
    """Run detectors and print findings."""
    db_path = get_db_path(db)
    df = load_transactions(db_path, account=account)

    rec = detect_monthly_recurring(df)
    if rec.empty:
        print("[yellow]No monthly recurring charges found yet (need ~3+ occurrences).[/yellow]")
    else:
        print("[bold green]Monthly recurring candidates:[/bold green]")
        print(rec.to_string(index=False))

    creep = detect_price_creep(df)
    if creep.empty:
        print("[yellow]No price creep found yet.[/yellow]")
    else:
        print("\n[bold green]Price creep candidates:[/bold green]")
        print(creep.to_string(index=False))

    t2p = detect_trial_to_paid(df)
    if t2p.empty:
        print("\n[yellow]No trial → paid patterns found yet.[/yellow]")
    else:
        print("\n[bold green]Trial → paid candidates:[/bold green]")
        print(t2p.to_string(index=False))


@app.command()
def report(
    account: str = typer.Option(..., help="Account label to report on"),
    out: str = typer.Option("report.html", help="Output HTML file"),
    db: str = typer.Option("expenseforensics.sqlite", help="SQLite DB file name"),
):
    """Generate an HTML report."""
    db_path = get_db_path(db)
    df = load_transactions(db_path, account=account)

    recurring = detect_monthly_recurring(df)
    creep = detect_price_creep(df)
    t2p = detect_trial_to_paid(df)

    html = build_html_report(
        account=account,
        recurring=recurring,
        price_creep=creep,
        trial_to_paid=t2p,
    )

    Path(out).write_text(html, encoding="utf-8")
    print(f"[green]Wrote report:[/green] {Path(out).resolve()}")


if __name__ == "__main__":
    app()
