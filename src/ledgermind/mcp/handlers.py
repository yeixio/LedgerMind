"""MCP tool implementations (sync; read-only YNAB)."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Literal

from ledgermind.domain.transactions import transaction_summary
from ledgermind.domain.types import float_to_milliunits
from ledgermind.services import spending as spending_svc
from ledgermind.services.debt import build_debts_view, simulate_debt_payoff
from ledgermind.services.forecasting import project_cashflow
from ledgermind.services.goals import project_savings_goal
from ledgermind.services.snapshot import build_budget_snapshot
from ledgermind.services.subscriptions import find_subscription_creep
from ledgermind.session import month_first_or_today, ynab_session


def get_budget_snapshot(month: str | None = None) -> dict[str, Any]:
    """High-level budget snapshot for the given calendar month (YYYY-MM) or current month."""
    as_of = month_first_or_today(month)
    with ynab_session() as sess:
        snap = build_budget_snapshot(sess.client, sess.budget_id, as_of=as_of)
        return snap.model_dump(mode="json")


def get_category_balances(month: str | None = None) -> dict[str, Any]:
    """Assigned, activity, and available per category for a month."""
    with ynab_session() as sess:
        return spending_svc.get_category_balances(sess.client, sess.budget_id, month=month)


def get_recent_transactions(
    limit: int = 50,
    category_id: str | None = None,
    payee_filter: str | None = None,
    since_date: str | None = None,
) -> dict[str, Any]:
    """Recent transactions with minimal fields (memo truncated)."""
    since: date = date.today() - timedelta(days=90)
    if since_date:
        since = date.fromisoformat(since_date[:10])
    pf = (payee_filter or "").lower()
    with ynab_session() as sess:
        txs = sess.client.list_transactions(sess.budget_id, since_date=since)
    out: list[dict[str, Any]] = []
    for t in txs:
        if category_id:
            cid = str(t.get("category_id") or t.get("categoryId") or "")
            if cid != category_id:
                continue
        row = transaction_summary(t)
        if pf:
            payee = (row.get("payee") or "") or ""
            if pf not in str(payee).lower():
                continue
        out.append(row)
    out.sort(key=lambda x: str(x.get("date", "")), reverse=True)
    lim = max(1, min(limit, 500))
    trimmed = out[:lim]
    return {"transactions": trimmed, "count": len(trimmed)}


def get_spending_by_category(month: str) -> dict[str, Any]:
    """Spending by category for YYYY-MM with percent of total and MoM change."""
    with ynab_session() as sess:
        return spending_svc.get_spending_by_category(sess.client, sess.budget_id, month=month)


def find_overspending(month: str | None = None) -> dict[str, Any]:
    """Categories with negative available."""
    with ynab_session() as sess:
        return spending_svc.find_overspending(sess.client, sess.budget_id, month=month)


def get_debts() -> dict[str, Any]:
    """Debt-like accounts with optional APR/minimums from local metadata file."""
    with ynab_session() as sess:
        meta = sess.settings.ledgermind_debt_metadata_file
        return build_debts_view(sess.client, sess.budget_id, metadata_path=meta)


def simulate_debt_payoff_tool(
    strategy: Literal["avalanche", "snowball"],
    extra_payment_milliunits: int,
    monthly_budget_buffer_milliunits: int | None = None,
) -> dict[str, Any]:
    """
    Debt payoff simulation. Amounts are YNAB milliunits (1000 = 1.00 in currency).
    extra_payment_milliunits is on top of minimum payments each month.
    monthly_budget_buffer_milliunits: optional affordability ceiling; defaults from
    LEDGERMIND_MINIMUM_BUFFER (interpreted as whole currency units, e.g. USD).
    """
    with ynab_session() as sess:
        meta = sess.settings.ledgermind_debt_metadata_file
        buf = monthly_budget_buffer_milliunits
        if buf is None:
            buf = float_to_milliunits(float(sess.settings.ledgermind_minimum_buffer))
        return simulate_debt_payoff(
            sess.client,
            sess.budget_id,
            strategy=strategy,
            extra_payment_milliunits=extra_payment_milliunits,
            monthly_budget_buffer_milliunits=buf,
            metadata_path=meta,
        )


def project_savings_goal_tool(
    target_amount_milliunits: int,
    monthly_contribution_milliunits: int,
    current_saved_milliunits: int = 0,
    target_date: str | None = None,
) -> dict[str, Any]:
    """Savings timeline and gap vs a target month (YYYY-MM). Amounts in milliunits."""
    return project_savings_goal(
        target_amount_milliunits=target_amount_milliunits,
        monthly_contribution_milliunits=monthly_contribution_milliunits,
        current_saved_milliunits=current_saved_milliunits,
        target_date=target_date,
    )


def project_cashflow_tool(
    months: int,
    income_adjustment_pct: float = 0.0,
    spending_adjustment_pct: float = 0.0,
    minimum_buffer_milliunits: int | None = None,
    lookback_months: int | None = None,
) -> dict[str, Any]:
    """Project on-budget cash using average income/spending from recent months."""
    with ynab_session() as sess:
        lb = lookback_months or sess.settings.ledgermind_default_lookback_months
        buf = minimum_buffer_milliunits
        if buf is None:
            buf = float_to_milliunits(float(sess.settings.ledgermind_minimum_buffer))
        return project_cashflow(
            sess.client,
            sess.budget_id,
            months=months,
            income_adjustment_pct=income_adjustment_pct,
            spending_adjustment_pct=spending_adjustment_pct,
            minimum_buffer_milliunits=buf,
            lookback_months=lb,
        )


def find_subscription_creep_tool(lookback_months: int | None = None) -> dict[str, Any]:
    """Heuristic recurring charges and amount creep."""
    with ynab_session() as sess:
        lb = lookback_months or sess.settings.ledgermind_default_lookback_months
        return find_subscription_creep(sess.client, sess.budget_id, lookback_months=lb)
