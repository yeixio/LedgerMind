"""Debt payoff simulation invariants."""

from datetime import date
from pathlib import Path
from typing import Any

import yaml

from ledgermind.api.ynab_client import YNABClient
from ledgermind.services.debt import simulate_debt_payoff


class _TwoDebtClient(YNABClient):
    def __init__(self) -> None:  # type: ignore[no-untyped-def]
        object.__init__(self)

    def close(self) -> None:
        return None

    def list_accounts(self, budget_id: str) -> list[dict[str, Any]]:
        return [
            {
                "id": "a-high",
                "name": "High APR",
                "type": "creditCard",
                "onBudget": True,
                "closed": False,
                "balance": -100_000,
                "clearedBalance": -100_000,
                "unclearedBalance": 0,
            },
            {
                "id": "a-low",
                "name": "Low APR",
                "type": "creditCard",
                "onBudget": True,
                "closed": False,
                "balance": -50_000,
                "clearedBalance": -50_000,
                "unclearedBalance": 0,
            },
        ]


def test_simulate_pays_off_with_metadata(tmp_path: Path) -> None:
    p = tmp_path / "debt.yaml"
    p.write_text(
        yaml.dump(
            {
                "accounts": {
                    "high_apr": {"apr": 24.0, "minimum_payment": 25},
                    "low_apr": {"apr": 12.0, "minimum_payment": 25},
                },
            },
        ),
        encoding="utf-8",
    )
    client = _TwoDebtClient()
    out = simulate_debt_payoff(
        client,
        "b1",
        strategy="avalanche",
        extra_payment_milliunits=50_000,
        monthly_budget_buffer_milliunits=500_000,
        metadata_path=p,
        max_months=120,
        as_of=date(2025, 1, 15),
    )
    assert out["payoff_months"] > 0
    assert out["payoff_months"] < 120
    assert out["total_interest_milliunits"] >= 0
