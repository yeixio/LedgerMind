"""Command-line interface."""

from __future__ import annotations

from datetime import date
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from ledgermind import __version__
from ledgermind.api.ynab_client import YNABClient
from ledgermind.cache.sqlite import clear_cache
from ledgermind.config import Settings, load_settings
from ledgermind.domain.types import milliunits_to_float
from ledgermind.exceptions import ConfigurationError, LedgerMindError, YNABAPIError
from ledgermind.logging import setup_logging
from ledgermind.services.snapshot import build_budget_snapshot

app = typer.Typer(no_args_is_help=True, add_completion=False)
console = Console(stderr=True)


def _budget_id_from_row(b: dict[str, Any]) -> str:
    return str(b.get("id", ""))


def resolve_budget_id(settings: Settings, client: YNABClient) -> str:
    if settings.ynab_budget_id:
        return settings.ynab_budget_id
    default = client.default_budget_id()
    if default:
        return default
    budgets = client.list_budgets()
    if not budgets:
        raise ConfigurationError("No budgets found for this YNAB token.")
    return _budget_id_from_row(budgets[0])


def _fmt_money(milliunits: int, iso: str | None) -> str:
    value = milliunits_to_float(milliunits)
    if iso:
        return f"{value:,.2f} {iso}"
    return f"{value:,.2f}"


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

    as_of = date.today()
    if month:
        try:
            y, m = month.split("-", 1)
            as_of = date(int(y), int(m), 1)
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


@app.command("clear-cache")
def clear_cache_cmd() -> None:
    """Remove local SQLite cache file when caching is enabled."""
    settings = load_settings()
    setup_logging(settings.ledgermind_log_level, debug_financial=settings.ledgermind_debug_log)
    msg = clear_cache(settings)
    console.print(msg)


@app.command("run-mcp")
def run_mcp() -> None:
    """Run the MCP server (Phase 3)."""
    console.print("[yellow]MCP server is not implemented yet (Phase 3).[/yellow]")
    raise typer.Exit(2)


def run() -> None:
    app()


if __name__ == "__main__":
    run()
