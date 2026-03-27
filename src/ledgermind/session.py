"""Shared YNAB client + budget resolution for CLI and MCP."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date

from ledgermind.api.ynab_client import YNABClient
from ledgermind.config import Settings, load_settings
from ledgermind.domain.budgets import active_budgets_only
from ledgermind.exceptions import ConfigurationError


def resolve_budget_id(settings: Settings, client: YNABClient) -> str:
    """
    Pick a budget for CLI/MCP: explicit YNAB_BUDGET_ID, else YNAB default if it is
    **active** (not archived/deleted), else first **active** budget in the list.
    """
    data = client.read_budgets_root()
    budgets = data.get("budgets") or []
    if not isinstance(budgets, list):
        budgets = []
    active = active_budgets_only(budgets)
    if settings.ynab_budget_id:
        return settings.ynab_budget_id
    db = data.get("default_budget")
    default_id: str | None = None
    if isinstance(db, dict) and db.get("id"):
        default_id = str(db["id"])
    if default_id and active and any(str(b.get("id")) == default_id for b in active):
        return default_id
    if active:
        return str(active[0].get("id", ""))
    if budgets:
        raise ConfigurationError(
            "No active budgets (all archived or deleted). Un-archive one in YNAB or set "
            "YNAB_BUDGET_ID to a specific budget id.",
        )
    raise ConfigurationError("No budgets found for this YNAB token.")


def resolve_web_budget_id(settings: Settings, client: YNABClient) -> str | None:
    """
    Same as resolve_budget_id, but when several active budgets exist and none is
    chosen, return None so the web UI can require an explicit pick.
    """
    data = client.read_budgets_root()
    budgets = data.get("budgets") or []
    if not isinstance(budgets, list):
        budgets = []
    active = active_budgets_only(budgets)
    if settings.ynab_budget_id:
        return settings.ynab_budget_id
    if len(active) == 1:
        return str(active[0].get("id", ""))
    if len(active) == 0:
        if budgets:
            raise ConfigurationError(
                "No active budgets (all archived or deleted). Un-archive one in YNAB.",
            )
        raise ConfigurationError("No budgets found for this YNAB token.")
    return None


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
