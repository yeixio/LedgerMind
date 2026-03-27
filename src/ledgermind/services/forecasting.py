"""Short-term cash-flow projection from recent budget months."""

from __future__ import annotations

from datetime import date
from typing import Any

from ledgermind.api.ynab_client import YNABClient
from ledgermind.domain.dates import month_starts_ending_at
from ledgermind.services.snapshot import build_budget_snapshot


def _month_income_milliunits(month_raw: dict[str, Any]) -> int:
    v = month_raw.get("income")
    if v is None:
        return 0
    return int(v)


def _month_spending_milliunits(month_raw: dict[str, Any]) -> int:
    total = 0
    for c in month_raw.get("categories", []) or []:
        act = c.get("activity")
        if act is None:
            continue
        a = int(act)
        if a < 0:
            total += -a
    return total


def project_cashflow(
    client: YNABClient,
    budget_id: str,
    *,
    months: int,
    income_adjustment_pct: float = 0.0,
    spending_adjustment_pct: float = 0.0,
    minimum_buffer_milliunits: int = 0,
    lookback_months: int = 6,
    starting_cash_milliunits: int | None = None,
) -> dict[str, Any]:
    """
    Project on-budget cash using average net (income - category outflows) from recent months.
    """
    end_month = date.today().replace(day=1)
    hist = month_starts_ending_at(end_month, lookback_months)
    incomes: list[int] = []
    spendings: list[int] = []
    for mm in hist:
        raw = client.get_month(budget_id, mm)
        incomes.append(_month_income_milliunits(raw))
        spendings.append(_month_spending_milliunits(raw))

    if not hist:
        return {
            "error": "no historic months",
            "projected_monthly_balances_milliunits": [],
            "months_at_risk": [],
            "assumptions": [],
        }

    avg_income = sum(incomes) // len(incomes)
    avg_spend = sum(spendings) // len(spendings)
    adj_income = int(avg_income * (1.0 + income_adjustment_pct / 100.0))
    adj_spend = int(avg_spend * (1.0 + spending_adjustment_pct / 100.0))
    net_monthly = adj_income - adj_spend

    if starting_cash_milliunits is None:
        snap = build_budget_snapshot(client, budget_id, as_of=date.today())
        cash0 = snap.total_cash_on_budget_milliunits
    else:
        cash0 = starting_cash_milliunits

    balances: list[dict[str, Any]] = []
    months_at_risk: list[int] = []
    bal = float(cash0)
    for m in range(1, months + 1):
        bal += net_monthly
        row = {"month_index": m, "projected_cash_milliunits": int(round(bal))}
        balances.append(row)
        if bal < minimum_buffer_milliunits:
            months_at_risk.append(m)

    return {
        "budget_id": budget_id,
        "lookback_months": lookback_months,
        "average_monthly_income_milliunits": avg_income,
        "average_monthly_spending_milliunits": avg_spend,
        "adjusted_monthly_income_milliunits": adj_income,
        "adjusted_monthly_spending_milliunits": adj_spend,
        "assumed_net_monthly_milliunits": net_monthly,
        "starting_cash_milliunits": cash0,
        "projected_monthly_balances_milliunits": balances,
        "months_at_risk": months_at_risk,
        "assumptions": [
            "Income uses YNAB month-level income; spending sums max(0, -category activity).",
            "Holds recent averages flat; does not model true bill timing or CC float.",
            "This is a scenario model, not a forecast of actual bank balances.",
        ],
    }
