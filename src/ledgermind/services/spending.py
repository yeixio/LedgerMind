"""Category spending and overspending from budget months."""

from __future__ import annotations

from datetime import date
from typing import Any

from ledgermind.api.ynab_client import YNABClient
from ledgermind.domain.dates import month_starts_ending_at
from ledgermind.domain.normalization import category_lookup_from_groups, normalize_category_month


def _parse_month(s: str) -> date:
    try:
        y, m = s.split("-", 1)
        return date(int(y), int(m), 1)
    except (ValueError, IndexError) as e:
        raise ValueError("month must be YYYY-MM") from e


def _categories_for_month(
    client: YNABClient,
    budget_id: str,
    month: date,
    lookup: dict[str, tuple[str, str | None]],
) -> list[dict[str, Any]]:
    month_raw = client.get_month(budget_id, month)
    rows: list[dict[str, Any]] = []
    for row in month_raw.get("categories", []) or []:
        if row.get("hidden"):
            continue
        cid = str(row.get("category_id") or row.get("categoryId") or row.get("id", ""))
        cname, gname = lookup.get(cid, ("(unknown)", None))
        cm = normalize_category_month(row, category_name=cname, category_group_name=gname)
        spend = max(0, -cm.activity_milliunits)
        rows.append(
            {
                "category_id": cm.category_id,
                "name": cm.name,
                "group": cm.category_group_name,
                "assigned_milliunits": cm.assigned_milliunits,
                "activity_milliunits": cm.activity_milliunits,
                "available_milliunits": cm.available_milliunits,
                "spending_milliunits": spend,
                "overspent": cm.available_milliunits < 0,
            },
        )
    return rows


def get_category_balances(
    client: YNABClient,
    budget_id: str,
    *,
    month: str | None = None,
) -> dict[str, Any]:
    """Per-category assigned / activity / available for a month (default: current)."""
    m = _parse_month(month) if month else date.today().replace(day=1)
    groups = client.list_category_groups(budget_id)
    lookup = category_lookup_from_groups(groups)
    rows = _categories_for_month(client, budget_id, m, lookup)
    return {
        "budget_id": budget_id,
        "month": m.isoformat(),
        "categories": rows,
    }


def get_spending_by_category(
    client: YNABClient,
    budget_id: str,
    *,
    month: str,
) -> dict[str, Any]:
    """Spending by category; percent of total and MoM delta when prior month exists."""
    m = _parse_month(month)
    groups = client.list_category_groups(budget_id)
    lookup = category_lookup_from_groups(groups)
    cur = _categories_for_month(client, budget_id, m, lookup)

    prev_m = date(m.year - 1, 12, 1) if m.month == 1 else date(m.year, m.month - 1, 1)
    try:
        prev_rows = _categories_for_month(client, budget_id, prev_m, lookup)
    except Exception:
        prev_rows = []
    prev_by_id = {r["category_id"]: r["spending_milliunits"] for r in prev_rows}

    total = sum(r["spending_milliunits"] for r in cur)
    cats: list[dict[str, Any]] = []
    for r in cur:
        s = r["spending_milliunits"]
        pct = (s / total) if total > 0 else 0.0
        prev_s = prev_by_id.get(r["category_id"], 0)
        cats.append(
            {
                "category_id": r["category_id"],
                "name": r["name"],
                "group": r["group"],
                "spending_milliunits": s,
                "percent_of_total": round(pct, 4),
                "change_vs_prior_month_milliunits": s - prev_s,
            },
        )
    cats.sort(key=lambda x: -x["spending_milliunits"])
    return {
        "budget_id": budget_id,
        "month": m.isoformat(),
        "total_spending_milliunits": total,
        "categories": cats,
        "assumptions": [
            "Spending is approximated as max(0, -category activity) for the month.",
        ],
    }


def find_overspending(
    client: YNABClient,
    budget_id: str,
    *,
    month: str | None = None,
) -> dict[str, Any]:
    """Categories with negative available (cash overspent)."""
    m = _parse_month(month) if month else date.today().replace(day=1)
    groups = client.list_category_groups(budget_id)
    lookup = category_lookup_from_groups(groups)
    rows = _categories_for_month(client, budget_id, m, lookup)
    overs: list[dict[str, Any]] = []
    for r in rows:
        if r["available_milliunits"] < 0:
            overs.append(
                {
                    "category_id": r["category_id"],
                    "name": r["name"],
                    "group": r["group"],
                    "amount_overspent_milliunits": -r["available_milliunits"],
                    "note": (
                        "Negative available usually needs covering from "
                        "another category or RTA."
                    ),
                },
            )
    return {
        "budget_id": budget_id,
        "month": m.isoformat(),
        "overspent_categories": overs,
        "count": len(overs),
    }


def spending_trend_summary(
    client: YNABClient,
    budget_id: str,
    *,
    end_month: date,
    lookback_months: int,
) -> dict[str, Any]:
    """Average monthly spending (outflow sum) over recent closed months."""
    groups = client.list_category_groups(budget_id)
    lookup = category_lookup_from_groups(groups)
    months = month_starts_ending_at(end_month, lookback_months)
    totals: list[int] = []
    for mm in months:
        rows = _categories_for_month(client, budget_id, mm, lookup)
        totals.append(sum(r["spending_milliunits"] for r in rows))
    avg = sum(totals) // len(totals) if totals else 0
    return {
        "months": [x.isoformat() for x in months],
        "monthly_total_spending_milliunits": totals,
        "average_monthly_spending_milliunits": avg,
    }
