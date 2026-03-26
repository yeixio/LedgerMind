"""Budget snapshot assembly (read-only)."""

from __future__ import annotations

from datetime import date
from typing import Any

from ledgermind.api.ynab_client import YNABClient
from ledgermind.domain.models import BudgetSnapshot
from ledgermind.domain.normalization import (
    category_lookup_from_groups,
    is_debt_like,
    normalize_account,
    normalize_budget_month,
    normalize_category_month,
)

# On-budget liquid accounts for "cash on budget" (exclude credit and loans).
_CASH_ACCOUNT_TYPES = frozenset({"checking", "savings", "cash", "moneyMarket"})


def _currency_iso(budget: dict[str, Any]) -> str | None:
    cf = budget.get("currency_format") or budget.get("currencyFormat")
    if isinstance(cf, dict):
        raw = cf.get("iso_code") or cf.get("isoCode")
        return str(raw) if raw else None
    return None


def _budget_name(budget: dict[str, Any]) -> str:
    return str(budget.get("name", ""))


def build_budget_snapshot(
    client: YNABClient,
    budget_id: str,
    *,
    as_of: date | None = None,
) -> BudgetSnapshot:
    """Load YNAB data and produce a high-level snapshot for the given calendar month."""
    today = date.today()
    as_of = as_of or today
    month_start = as_of.replace(day=1)

    budget = client.get_budget(budget_id)
    groups = client.list_category_groups(budget_id)
    lookup = category_lookup_from_groups(groups)

    accounts = [normalize_account(a) for a in client.list_accounts(budget_id)]
    cash_total = sum(
        a.balance_milliunits
        for a in accounts
        if a.on_budget and not a.closed and a.account_type in _CASH_ACCOUNT_TYPES
    )
    debts = [a for a in accounts if is_debt_like(a) and not a.closed]

    month_raw = client.get_month(budget_id, month_start)
    month_summary = normalize_budget_month(month_raw)

    total_assigned = 0
    total_available = 0
    overspent = 0

    for row in month_raw.get("categories", []) or []:
        if row.get("hidden") or row.get("Hidden"):
            continue
        cid = str(row.get("category_id") or row.get("categoryId") or row.get("id", ""))
        cname, gname = lookup.get(cid, ("(unknown category)", None))
        cm = normalize_category_month(row, category_name=cname, category_group_name=gname)
        total_assigned += cm.assigned_milliunits
        total_available += cm.available_milliunits
        if cm.available_milliunits < 0:
            overspent += 1

    return BudgetSnapshot(
        budget_id=budget_id,
        budget_name=_budget_name(budget),
        as_of=as_of,
        currency_format_iso=_currency_iso(budget),
        total_cash_on_budget_milliunits=cash_total,
        total_assigned_milliunits=total_assigned,
        total_available_milliunits=total_available,
        overspent_category_count=overspent,
        to_be_budgeted_milliunits=month_summary.to_be_budgeted_milliunits,
        age_of_money=month_summary.age_of_money,
        debt_accounts=debts,
    )
