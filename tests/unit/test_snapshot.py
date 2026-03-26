"""Snapshot service tests."""

from datetime import date
from typing import Any

from ledgermind.api.ynab_client import YNABClient
from ledgermind.services.snapshot import build_budget_snapshot


class _FakeYNAB(YNABClient):
    """Minimal fake returning canned payloads (no HTTP)."""

    def __init__(self) -> None:  # type: ignore[no-untyped-def]
        object.__init__(self)

    def close(self) -> None:
        return None

    def get_budget(self, budget_id: str) -> dict[str, Any]:
        return {
            "id": budget_id,
            "name": "Test Budget",
            "currencyFormat": {"isoCode": "USD"},
        }

    def list_category_groups(self, budget_id: str) -> list[dict[str, Any]]:
        return [
            {
                "id": "g1",
                "name": "Monthly",
                "categories": [{"id": "c1", "name": "Groceries"}],
            },
        ]

    def list_accounts(self, budget_id: str) -> list[dict[str, Any]]:
        return [
            {
                "id": "acct-checking",
                "name": "Checking",
                "type": "checking",
                "onBudget": True,
                "closed": False,
                "balance": 50_000,
                "clearedBalance": 50_000,
                "unclearedBalance": 0,
            },
            {
                "id": "acct-cc",
                "name": "Card",
                "type": "creditCard",
                "onBudget": True,
                "closed": False,
                "balance": -12_000,
                "clearedBalance": -12_000,
                "unclearedBalance": 0,
            },
        ]

    def get_month(self, budget_id: str, month: date) -> dict[str, Any]:
        return {
            "month": month.strftime("%Y-%m-%d"),
            "toBeBudgeted": 1000,
            "ageOfMoney": 10,
            "categories": [
                {
                    "categoryId": "c1",
                    "budgeted": 400_000,
                    "activity": -350_000,
                    "balance": 50_000,
                    "hidden": False,
                },
            ],
        }


def test_build_budget_snapshot() -> None:
    client = _FakeYNAB()
    snap = build_budget_snapshot(client, "b1", as_of=date(2025, 3, 15))
    assert snap.budget_name == "Test Budget"
    assert snap.total_cash_on_budget_milliunits == 50_000
    assert snap.overspent_category_count == 0
    assert len(snap.debt_accounts) == 1
    assert snap.debt_accounts[0].name == "Card"
