"""Shared YNAB client + budget resolution for CLI and MCP."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date

from ledgermind.api.ynab_client import YNABClient
from ledgermind.config import Settings, load_settings


def resolve_budget_id(settings: Settings, client: YNABClient) -> str:
    if settings.ynab_budget_id:
        return settings.ynab_budget_id
    default = client.default_budget_id()
    if default:
        return default
    budgets = client.list_budgets()
    if not budgets:
        from ledgermind.exceptions import ConfigurationError

        raise ConfigurationError("No budgets found for this YNAB token.")
    return str(budgets[0].get("id", ""))


@dataclass
class YnabSession:
    client: YNABClient
    budget_id: str
    settings: Settings


@contextmanager
def ynab_session(settings: Settings | None = None) -> Iterator[YnabSession]:
    s = settings or load_settings()
    token = s.require_ynab_token()
    with YNABClient(token) as client:
        bid = resolve_budget_id(s, client)
        yield YnabSession(client=client, budget_id=bid, settings=s)


def month_first_or_today(month: str | None) -> date:
    """First day of YYYY-MM, or today if month is None."""
    if not month:
        return date.today()
    try:
        y, m = month.split("-", 1)
        return date(int(y), int(m), 1)
    except ValueError as e:
        raise ValueError("month must be YYYY-MM") from e
