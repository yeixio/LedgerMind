"""Map YNAB API payloads into domain models."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from ledgermind.domain.models import Account, BudgetMonthSummary, CategoryMonth

_DEBT_TYPES = frozenset({"creditCard", "lineOfCredit", "loan", "mortgage", "otherLiability"})


def _snake_to_camel(key: str) -> str:
    parts = key.split("_")
    return parts[0] + "".join(p.title() for p in parts[1:])


def _get(raw: dict[str, Any], snake_key: str) -> Any:
    """YNAB JSON uses camelCase; accept snake_case for readability in code."""
    if snake_key in raw:
        return raw[snake_key]
    camel = _snake_to_camel(snake_key)
    if camel in raw:
        return raw[camel]
    raise KeyError(snake_key)


def _parse_ynab_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def normalize_account(raw: dict[str, Any]) -> Account:
    return Account(
        id=str(_get(raw, "id")),
        name=str(_get(raw, "name")),
        account_type=str(_get(raw, "type")),
        on_budget=bool(_get(raw, "on_budget")),
        closed=bool(_get(raw, "closed")),
        balance_milliunits=int(_get(raw, "balance")),
        cleared_balance_milliunits=int(_get(raw, "cleared_balance")),
        uncleared_balance_milliunits=int(_get(raw, "uncleared_balance")),
    )


def is_debt_like(account: Account) -> bool:
    return account.account_type in _DEBT_TYPES


def normalize_category_month(
    raw: dict[str, Any],
    *,
    category_name: str,
    category_group_name: str | None,
) -> CategoryMonth:
    cid = raw.get("category_id") or raw.get("categoryId") or _get(raw, "id")
    return CategoryMonth(
        category_id=str(cid),
        name=category_name,
        category_group_name=category_group_name,
        assigned_milliunits=int(_get(raw, "budgeted")),
        activity_milliunits=int(_get(raw, "activity")),
        available_milliunits=int(_get(raw, "balance")),
        hidden=bool(raw.get("hidden", False)),
    )


def normalize_budget_month(raw: dict[str, Any]) -> BudgetMonthSummary:
    def opt_int(snake: str, default: int = 0) -> int:
        try:
            return int(_get(raw, snake))
        except KeyError:
            return default

    age = raw.get("age_of_money", raw.get("ageOfMoney"))
    return BudgetMonthSummary(
        month=_parse_ynab_date(str(_get(raw, "month"))),
        to_be_budgeted_milliunits=int(_get(raw, "to_be_budgeted")),
        age_of_money=int(age) if age is not None else None,
        income_milliunits=opt_int("income", 0),
        budgeted_milliunits=opt_int("budgeted", 0),
        activity_milliunits=opt_int("activity", 0),
    )


def category_lookup_from_groups(groups: list[dict[str, Any]]) -> dict[str, tuple[str, str | None]]:
    """Map category id -> (name, group_name)."""
    out: dict[str, tuple[str, str | None]] = {}
    for g in groups:
        gname = str(g.get("name", "")) or None
        for c in g.get("categories", []):
            cid = str(_get(c, "id"))
            cname = str(_get(c, "name"))
            out[cid] = (cname, gname)
    return out
