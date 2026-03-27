"""Heuristic recurring charge detection from transactions."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from statistics import mean
from typing import Any

from ledgermind.api.ynab_client import YNABClient


def _parse_tx_date(s: str) -> date:
    return datetime.strptime(s[:10], "%Y-%m-%d").date()


def _payee_key(t: dict[str, Any]) -> str:
    pid = t.get("payee_id") or t.get("payeeId")
    pname = t.get("payee_name") or t.get("payeeName") or ""
    return str(pid or pname or "unknown")


def _amount_milliunits(t: dict[str, Any]) -> int:
    v = t.get("amount")
    return int(v) if v is not None else 0


def find_subscription_creep(
    client: YNABClient,
    budget_id: str,
    *,
    lookback_months: int = 6,
) -> dict[str, Any]:
    """
    Group outflows by payee; flag recurring-ish patterns (similar amounts, ~monthly cadence).
    """
    today = date.today()
    start = date(today.year, today.month, 1)
    for _ in range(lookback_months):
        if start.month == 1:
            start = date(start.year - 1, 12, 1)
        else:
            start = date(start.year, start.month - 1, 1)

    txs = client.list_transactions(budget_id, since_date=start)
    by_payee: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for t in txs:
        amt = _amount_milliunits(t)
        if amt >= 0:
            continue
        if t.get("deleted"):
            continue
        by_payee[_payee_key(t)].append(t)

    candidates: list[dict[str, Any]] = []
    for key, items in by_payee.items():
        if len(items) < 3:
            continue
        amounts = [abs(_amount_milliunits(x)) for x in items]
        am = mean(amounts)
        if am <= 0:
            continue
        rel_spread = max(amounts) - min(amounts)
        if rel_spread / am > 0.12:
            continue
        dated = (_parse_tx_date(str(x.get("date", ""))) for x in items if x.get("date"))
        dates_sorted = sorted(dated)
        if len(dates_sorted) < 3:
            continue
        gaps = [
            (dates_sorted[i] - dates_sorted[i - 1]).days for i in range(1, len(dates_sorted))
        ]
        avg_gap = mean(gaps) if gaps else 0
        if not (20 <= avg_gap <= 40):
            continue
        first_amt = amounts[0]
        last_amt = amounts[-1]
        creep = last_amt - first_amt
        flagged = creep > max(5000, int(0.05 * first_amt))
        label = items[0].get("payee_name") or items[0].get("payeeName") or key
        candidates.append(
            {
                "payee": str(label),
                "occurrences": len(items),
                "estimated_cadence_days": round(avg_gap, 1),
                "typical_amount_milliunits": int(round(am)),
                "first_amount_milliunits": first_amt,
                "latest_amount_milliunits": last_amt,
                "amount_change_milliunits": creep,
                "flagged_increase": flagged,
            },
        )

    candidates.sort(key=lambda x: (-x["occurrences"], x["payee"]))
    return {
        "budget_id": budget_id,
        "lookback_months": lookback_months,
        "recurring_charge_candidates": candidates,
        "assumptions": [
            "Heuristic: similar outflow amounts and ~monthly spacing; "
            "expect false positives/negatives.",
            "Transfers and split transactions may confuse grouping.",
        ],
    }
