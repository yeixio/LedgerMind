"""Command-line interface."""

from __future__ import annotations

import json
from datetime import date
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from ledgermind import __version__
from ledgermind.api.ynab_client import YNABClient
from ledgermind.cache.sqlite import clear_cache
from ledgermind.config import load_settings
from ledgermind.domain.types import float_to_milliunits, milliunits_to_float
from ledgermind.exceptions import ConfigurationError, LedgerMindError, YNABAPIError
from ledgermind.logging import setup_logging
from ledgermind.services.debt import build_debts_view
from ledgermind.services.forecasting import project_cashflow
from ledgermind.services.goals import project_savings_goal
from ledgermind.services.snapshot import build_budget_snapshot
from ledgermind.session import month_first_or_today, resolve_budget_id

app = typer.Typer(no_args_is_help=True, add_completion=False)
console = Console(stderr=True)


def _budget_id_from_row(b: dict[str, Any]) -> str:
    return str(b.get("id", ""))


def _fmt_money(milliunits: int, iso: str | None) -> str:
    value = milliunits_to_float(milliunits)
    if iso:
        return f"{value:,.2f} {iso}"
    return f"{value:,.2f}"


def _print_json(data: object) -> None:
    print(json.dumps(data, indent=2, default=str))


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", help="Print version and exit."),
) -> None:
    if version:
        console.print(__version__)
        raise typer.Exit(0)


@app.command()
def doctor() -> None:
    """Check configuration and YNAB connectivity."""
    settings = load_settings()
    setup_logging(settings.ledgermind_log_level, debug_financial=settings.ledgermind_debug_log)
    console.print(f"LedgerMind {__version__}")
    try:
        token = settings.require_ynab_token()
    except ConfigurationError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(2) from e

    masked = "(empty)"
    if token:
        masked = f"…{token[-4:]}" if len(token) > 4 else "(set)"
    console.print(f"YNAB token: {masked}")
    console.print(f"Budget ID: {settings.ynab_budget_id or '(auto: default or first)'}")

    try:
        with YNABClient(token) as client:
            budgets = client.list_budgets()
    except YNABAPIError as e:
        console.print(f"[red]YNAB error:[/red] {e}")
        raise typer.Exit(1) from e

    console.print(f"[green]OK[/green] — reachable; {len(budgets)} budget(s).")


@app.command("list-budgets")
def list_budgets() -> None:
    """List budgets visible to the token."""
    settings = load_settings()
    setup_logging(settings.ledgermind_log_level, debug_financial=settings.ledgermind_debug_log)
    try:
        token = settings.require_ynab_token()
    except ConfigurationError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(2) from e

    try:
        with YNABClient(token) as client:
            budgets = client.list_budgets()
    except YNABAPIError as e:
        console.print(f"[red]YNAB error:[/red] {e}")
        raise typer.Exit(1) from e

    table = Table(title="YNAB budgets")
    table.add_column("Name")
    table.add_column("ID")
    for b in budgets:
        table.add_row(str(b.get("name", "")), _budget_id_from_row(b))
    console.print(table)


@app.command()
def snapshot(
    month: str | None = typer.Option(
        None,
        "--month",
        help="Month as YYYY-MM (default: current month).",
    ),
) -> None:
    """Print a high-level budget snapshot for the selected month."""
    settings = load_settings()
    setup_logging(settings.ledgermind_log_level, debug_financial=settings.ledgermind_debug_log)
    try:
        token = settings.require_ynab_token()
    except ConfigurationError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(2) from e

    try:
        as_of = month_first_or_today(month) if month else date.today()
    except ValueError as e:
        console.print("[red]Use --month YYYY-MM[/red]")
        raise typer.Exit(2) from e

    try:
        with YNABClient(token) as client:
            budget_id = resolve_budget_id(settings, client)
            snap = build_budget_snapshot(client, budget_id, as_of=as_of)
    except (YNABAPIError, LedgerMindError) as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1) from e

    iso = snap.currency_format_iso
    console.print(f"[bold]{snap.budget_name}[/bold] ({snap.budget_id})")
    console.print(f"As of: {snap.as_of.isoformat()}")
    console.print(f"Cash on budget: {_fmt_money(snap.total_cash_on_budget_milliunits, iso)}")
    console.print(f"Assigned (month): {_fmt_money(snap.total_assigned_milliunits, iso)}")
    console.print(f"Available (month): {_fmt_money(snap.total_available_milliunits, iso)}")
    console.print(f"To be budgeted: {_fmt_money(snap.to_be_budgeted_milliunits, iso)}")
    if snap.age_of_money is not None:
        console.print(f"Age of money: {snap.age_of_money} days")
    console.print(f"Overspent categories: {snap.overspent_category_count}")
    if snap.debt_accounts:
        console.print("[bold]Debt / credit (on books)[/bold]")
        for a in snap.debt_accounts:
            line = f"  - {a.name}: {_fmt_money(a.balance_milliunits, iso)} ({a.account_type})"
            console.print(line)


@app.command()
def debts() -> None:
    """Print debt accounts as JSON (see LEDGERMIND_DEBT_METADATA_FILE for APR/mins)."""
    settings = load_settings()
    setup_logging(settings.ledgermind_log_level, debug_financial=settings.ledgermind_debug_log)
    try:
        token = settings.require_ynab_token()
    except ConfigurationError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(2) from e
    try:
        with YNABClient(token) as client:
            bid = resolve_budget_id(settings, client)
            meta = settings.ledgermind_debt_metadata_file
            data = build_debts_view(client, bid, metadata_path=meta)
    except (YNABAPIError, LedgerMindError) as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1) from e
    _print_json(data)


@app.command()
def cashflow(
    months: int = typer.Option(6, "--months", "-m", help="Months to project forward."),
    income_pct: float = typer.Option(0.0, "--income-pct", help="Income adjustment %."),
    spend_pct: float = typer.Option(0.0, "--spend-pct", help="Spending adjustment %."),
) -> None:
    """Project on-budget cash from recent average income/spending (JSON)."""
    settings = load_settings()
    setup_logging(settings.ledgermind_log_level, debug_financial=settings.ledgermind_debug_log)
    try:
        token = settings.require_ynab_token()
    except ConfigurationError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(2) from e
    buf = float_to_milliunits(float(settings.ledgermind_minimum_buffer))
    try:
        with YNABClient(token) as client:
            bid = resolve_budget_id(settings, client)
            data = project_cashflow(
                client,
                bid,
                months=months,
                income_adjustment_pct=income_pct,
                spending_adjustment_pct=spend_pct,
                minimum_buffer_milliunits=buf,
                lookback_months=settings.ledgermind_default_lookback_months,
            )
    except (YNABAPIError, LedgerMindError) as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1) from e
    _print_json(data)


@app.command()
def goal(
    target: float = typer.Option(..., "--target", help="Target amount (currency units, e.g. USD)."),
    monthly: float = typer.Option(..., "--monthly", help="Monthly contribution (currency units)."),
    saved: float = typer.Option(0.0, "--saved", help="Already saved (currency units)."),
    by_month: str | None = typer.Option(
        None,
        "--by-month",
        help="Target month YYYY-MM for required contribution gap.",
    ),
) -> None:
    """Savings goal projection (JSON). Amounts are whole currency units."""
    settings = load_settings()
    setup_logging(settings.ledgermind_log_level, debug_financial=settings.ledgermind_debug_log)
    _ = settings  # token not needed for pure math
    data = project_savings_goal(
        target_amount_milliunits=float_to_milliunits(target),
        monthly_contribution_milliunits=float_to_milliunits(monthly),
        current_saved_milliunits=float_to_milliunits(saved),
        target_date=by_month,
    )
    _print_json(data)


@app.command("clear-cache")
def clear_cache_cmd() -> None:
    """Remove local SQLite cache file when caching is enabled."""
    settings = load_settings()
    setup_logging(settings.ledgermind_log_level, debug_financial=settings.ledgermind_debug_log)
    msg = clear_cache(settings)
    console.print(msg)


@app.command("run-mcp")
def run_mcp() -> None:
    """Run the MCP server (stdio)."""
    from ledgermind.mcp.server import run_stdio_server

    run_stdio_server()


@app.command("serve")
def serve(
    host: str = typer.Option(
        "127.0.0.1",
        "--host",
        help="Bind address (default: loopback only).",
    ),
    port: int = typer.Option(8765, "--port", "-p", help="HTTP port for the web UI."),
) -> None:
    """Start the local web UI (FastAPI + static assets on loopback)."""
    try:
        import uvicorn
    except ImportError as e:
        console.print('[red]Install API extras:[/red] pip install -e ".[api]"')
        raise typer.Exit(2) from e
    try:
        from ledgermind.web.app import create_app
    except ImportError as e:
        console.print('[red]Install API extras:[/red] pip install -e ".[api]"')
        raise typer.Exit(2) from e

    console.print(f"LedgerMind web UI — http://{host}:{port}/")
    console.print("Press Ctrl+C to stop.")
    uvicorn.run(create_app(), host=host, port=port, log_level="info")


def run() -> None:
    app()


if __name__ == "__main__":
    run()
