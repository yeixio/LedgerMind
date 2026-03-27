"""MCP handler output shapes (mocked YNAB session)."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import date, timedelta
from typing import Any

import pytest

from ledgermind.config import Settings
from ledgermind.mcp import handlers as h
from ledgermind.session import YnabSession


class _FakeYnab:
    """Minimal client for handler tests."""

    def get_budget(self, budget_id: str) -> dict[str, Any]:
        return {"name": "Test Budget", "currencyFormat": {"isoCode": "USD"}}

    def list_category_groups(self, budget_id: str) -> list[dict[str, Any]]:
        return [
            {
                "id": "g1",
                "name": "Monthly",
                "categories": [{"id": "cat-1", "name": "Food"}, {"id": "cat-2", "name": "Bills"}],
            },
        ]

    def list_accounts(self, budget_id: str) -> list[dict[str, Any]]:
        return [
            {
                "id": "chk",
                "name": "Checking",
                "type": "checking",
                "onBudget": True,
                "closed": False,
                "balance": 5_000_000,
                "clearedBalance": 5_000_000,
                "unclearedBalance": 0,
            },
            {
                "id": "cc",
                "name": "Visa",
                "type": "creditCard",
                "onBudget": True,
                "closed": False,
                "balance": -2_000_000,
                "clearedBalance": -2_000_000,
                "unclearedBalance": 0,
            },
        ]

    def get_month(self, budget_id: str, month: date) -> dict[str, Any]:
        return {
            "month": month.strftime("%Y-%m-%d"),
            "toBeBudgeted": 50_000,
            "ageOfMoney": 12,
            "income": 6_000_000,
            "categories": [
                {
                    "categoryId": "cat-1",
                    "budgeted": 300_000,
                    "activity": -200_000,
                    "balance": 100_000,
                    "hidden": False,
                },
                {
                    "categoryId": "cat-2",
                    "budgeted": 0,
                    "activity": -50_000,
                    "balance": -5_000,
                    "hidden": False,
                },
            ],
        }

    def list_transactions(
        self,
        budget_id: str,
        *,
        since_date: date | None = None,
    ) -> list[dict[str, Any]]:
        base = date(2025, 1, 10)
        out: list[dict[str, Any]] = []
        for i in range(4):
            d = base + timedelta(days=28 * i)
            out.append(
                {
                    "id": f"t{i}",
                    "date": d.isoformat(),
                    "amount": -10_000,
                    "payeeName": "SubSvc",
                    "categoryId": "cat-1",
                    "memo": "x",
                    "deleted": False,
                },
            )
        return out


@pytest.fixture
def fake_settings() -> Settings:
    return Settings.model_construct(
        ynab_access_token="t",
        ynab_budget_id="b1",
        ledgermind_minimum_buffer=1000,
        ledgermind_default_lookback_months=3,
        ledgermind_debt_metadata_file=None,
    )


@pytest.fixture
def mock_ynab_session(monkeypatch: pytest.MonkeyPatch, fake_settings: Settings) -> None:
    @contextmanager
    def _ynab_session(settings: Settings | None = None) -> Any:
        _ = settings
        yield YnabSession(
            client=_FakeYnab(),
            budget_id="b1",
            settings=fake_settings,
        )

    monkeypatch.setattr(h, "ynab_session", _ynab_session)


def test_get_budget_snapshot_keys(mock_ynab_session: None) -> None:
    out = h.get_budget_snapshot(month="2025-03")
    assert out["budget_id"] == "b1"
    assert "total_cash_on_budget_milliunits" in out
    assert "debt_accounts" in out


def test_get_category_balances_keys(mock_ynab_session: None) -> None:
    out = h.get_category_balances(month="2025-03")
    assert out["budget_id"] == "b1"
    assert isinstance(out["categories"], list)
    assert out["categories"][0]["name"] == "Food"


def test_get_recent_transactions_keys(mock_ynab_session: None) -> None:
    out = h.get_recent_transactions(limit=10)
    assert "transactions" in out and "count" in out
    assert out["count"] <= 10


def test_get_spending_by_category_keys(mock_ynab_session: None) -> None:
    out = h.get_spending_by_category(month="2025-03")
    assert "total_spending_milliunits" in out
    assert isinstance(out["categories"], list)


def test_find_overspending_keys(mock_ynab_session: None) -> None:
    out = h.find_overspending(month="2025-03")
    assert "overspent_categories" in out
    assert out["count"] >= 1


def test_get_debts_keys(mock_ynab_session: None) -> None:
    out = h.get_debts()
    assert "debts" in out
    assert any(d["name"] == "Visa" for d in out["debts"])


def test_simulate_debt_payoff_keys(mock_ynab_session: None) -> None:
    out = h.simulate_debt_payoff_tool(strategy="avalanche", extra_payment_milliunits=50_000)
    assert "payoff_months" in out
    assert "assumptions" in out


def test_project_savings_goal_keys() -> None:
    out = h.project_savings_goal_tool(
        target_amount_milliunits=1_000_000,
        monthly_contribution_milliunits=100_000,
    )
    assert "remaining_milliunits" in out
    assert "assumptions" in out


def test_project_cashflow_keys(mock_ynab_session: None) -> None:
    out = h.project_cashflow_tool(months=3)
    assert "projected_monthly_balances_milliunits" in out
    assert "assumptions" in out


def test_find_subscription_creep_keys(mock_ynab_session: None) -> None:
    out = h.find_subscription_creep_tool(lookback_months=6)
    assert "recurring_charge_candidates" in out
    assert "assumptions" in out


def test_registry_lists_ten_tools() -> None:
    from ledgermind.mcp.registry import V1_TOOL_NAMES

    assert len(V1_TOOL_NAMES) == 10


def test_fastmcp_registers_all_v1_tools() -> None:
    from ledgermind.mcp.registry import V1_TOOL_NAMES
    from ledgermind.mcp.server import create_mcp_app

    app = create_mcp_app()
    registered = {t.name for t in app._tool_manager.list_tools()}
    assert registered == set(V1_TOOL_NAMES)
