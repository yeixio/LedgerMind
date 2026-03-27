"""Debt listing and payoff simulation (educational model, not advice)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Literal

from ledgermind.api.ynab_client import YNABClient
from ledgermind.domain.normalization import is_debt_like, normalize_account
from ledgermind.services.debt_metadata import load_debt_metadata, lookup_debt_meta


def _owed_milliunits(balance_milliunits: int) -> int:
    """Treat negative YNAB balance as amount owed on typical credit accounts."""
    if balance_milliunits < 0:
        return -balance_milliunits
    return max(0, balance_milliunits)


def _default_minimum_payment(owed_milliunits: int) -> int:
    return max(int(owed_milliunits * 0.02), 25_000)


@dataclass
class _SimAccount:
    account_id: str
    name: str
    apr_annual_pct: float
    minimum_payment_milliunits: int
    balance_milliunits: float  # owed, positive; float for fractional interest


def build_debts_view(
    client: YNABClient,
    budget_id: str,
    *,
    metadata_path: Path | str | None = None,
) -> dict[str, Any]:
    """Structured debt account list for MCP/CLI."""
    path = Path(metadata_path) if metadata_path else None
    meta_map = load_debt_metadata(path)
    accounts = [normalize_account(a) for a in client.list_accounts(budget_id)]
    debts = [a for a in accounts if is_debt_like(a) and not a.closed]
    rows: list[dict[str, Any]] = []
    for a in debts:
        owed = _owed_milliunits(a.balance_milliunits)
        m = lookup_debt_meta(a.id, a.name, meta_map)
        rows.append(
            {
                "account_id": a.id,
                "name": a.name,
                "account_type": a.account_type,
                "balance_milliunits": a.balance_milliunits,
                "owed_milliunits": owed,
                "apr_annual_pct": m.apr_annual_pct if m else None,
                "minimum_payment_milliunits": m.minimum_payment_milliunits if m else None,
            },
        )
    return {
        "budget_id": budget_id,
        "debts": rows,
        "assumptions": [
            "APR and minimums come from optional local debt metadata when configured.",
            "When missing, minimum defaults to max(2% of balance, $25) for simulation only.",
        ],
    }


def simulate_debt_payoff(
    client: YNABClient,
    budget_id: str,
    *,
    strategy: Literal["avalanche", "snowball"],
    extra_payment_milliunits: int,
    monthly_budget_buffer_milliunits: int = 0,
    metadata_path: Path | str | None = None,
    max_months: int = 600,
    as_of: date | None = None,
) -> dict[str, Any]:
    """
    Simple monthly interest + payment waterfall model.

    Interest accrues at APR/12 on each balance, then minimums are paid, then extra
    is applied to avalanche (highest APR) or snowball (smallest balance) priority.
    """
    path = Path(metadata_path) if metadata_path else None
    meta_map = load_debt_metadata(path)
    accounts = [normalize_account(a) for a in client.list_accounts(budget_id)]
    debts_raw = [a for a in accounts if is_debt_like(a) and not a.closed]

    sim_accounts: list[_SimAccount] = []
    warnings: list[str] = []
    for a in debts_raw:
        owed = _owed_milliunits(a.balance_milliunits)
        if owed <= 0:
            continue
        meta = lookup_debt_meta(a.id, a.name, meta_map)
        if meta is None:
            warnings.append(f"No debt metadata entry for '{a.name}'; APR assumed 0%.")
            apr = 0.0
        else:
            apr = meta.apr_annual_pct
        min_pay = (
            meta.minimum_payment_milliunits
            if meta and meta.minimum_payment_milliunits > 0
            else 0
        )
        if min_pay <= 0:
            min_pay = _default_minimum_payment(owed)
            msg = (
                f"No minimum_payment for '{a.name}'; "
                "using default max(2% owed, $25) for simulation."
            )
            warnings.append(msg)
        sim_accounts.append(
            _SimAccount(
                account_id=a.id,
                name=a.name,
                apr_annual_pct=apr,
                minimum_payment_milliunits=min_pay,
                balance_milliunits=float(owed),
            ),
        )

    if not sim_accounts:
        return {
            "strategy": strategy,
            "payoff_months": 0,
            "projected_payoff_date": None,
            "total_interest_milliunits": 0,
            "warnings": warnings + ["No debt balances to simulate."],
            "assumptions": _sim_assumptions(),
            "monthly_payment_total_milliunits": extra_payment_milliunits,
        }

    total_minimum = sum(d.minimum_payment_milliunits for d in sim_accounts)
    total_payment = total_minimum + extra_payment_milliunits
    if monthly_budget_buffer_milliunits > 0 and total_payment > monthly_budget_buffer_milliunits:
        warnings.append(
            "Total debt payments (minimums + extra) exceed the configured monthly_budget_buffer; "
            "review affordability.",
        )

    total_interest = 0.0
    month_idx = 0
    schedule_tail: list[dict[str, Any]] = []

    while month_idx < max_months and any(d.balance_milliunits > 0.01 for d in sim_accounts):
        month_idx += 1
        # Accrue interest at month start
        month_interest = 0.0
        for d in sim_accounts:
            if d.balance_milliunits <= 0:
                continue
            intr = d.balance_milliunits * (d.apr_annual_pct / 100.0 / 12.0)
            intr_r = round(intr)
            d.balance_milliunits += intr_r
            month_interest += intr_r
        total_interest += month_interest

        pool = float(total_payment)
        # Pay minimums
        for d in sim_accounts:
            if d.balance_milliunits <= 0:
                continue
            pay = min(float(d.minimum_payment_milliunits), d.balance_milliunits, pool)
            d.balance_milliunits -= pay
            pool -= pay

        # Apply remaining to strategy priority
        while pool > 0.01:
            active = [d for d in sim_accounts if d.balance_milliunits > 0.01]
            if not active:
                break
            if strategy == "avalanche":
                target = max(active, key=lambda x: x.apr_annual_pct)
            else:
                target = min(active, key=lambda x: x.balance_milliunits)
            pay = min(pool, target.balance_milliunits)
            target.balance_milliunits -= pay
            pool -= pay

        any_balance = any(d.balance_milliunits > 0.01 for d in sim_accounts)
        if month_idx <= 3 or month_idx % 12 == 0 or not any_balance:
            schedule_tail.append(
                {
                    "month_index": month_idx,
                    "remaining_total_milliunits": int(
                        sum(max(0.0, d.balance_milliunits) for d in sim_accounts),
                    ),
                    "interest_this_month_milliunits": int(month_interest),
                },
            )

    today = as_of or date.today()
    # Approximate payoff calendar month
    y, mo = today.year, today.month
    for _ in range(month_idx):
        mo += 1
        if mo > 12:
            mo = 1
            y += 1
    payoff = date(y, mo, 1) if month_idx > 0 and month_idx < max_months else None
    if month_idx >= max_months:
        warnings.append(f"Simulation stopped after {max_months} months; debts may remain.")

    return {
        "strategy": strategy,
        "extra_payment_milliunits": extra_payment_milliunits,
        "total_minimum_payments_milliunits": total_minimum,
        "monthly_payment_total_milliunits": total_payment,
        "payoff_months": month_idx,
        "projected_payoff_date": payoff.isoformat() if payoff else None,
        "total_interest_milliunits": int(round(total_interest)),
        "monthly_schedule_summary": schedule_tail[-6:],
        "warnings": warnings,
        "assumptions": _sim_assumptions(),
    }


def _sim_assumptions() -> list[str]:
    return [
        "Model is deterministic and simplified: monthly compounding at APR/12, no new charges.",
        "Does not model grace periods, varying statement dates, or promo rates.",
        "This is a planning illustration, not a lending or legal guarantee.",
    ]
