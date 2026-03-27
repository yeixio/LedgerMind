"""Budget list filtering."""

from __future__ import annotations

from ledgermind.domain.budgets import active_budgets_only, is_budget_row_active


def test_is_budget_row_active_defaults_true() -> None:
    assert is_budget_row_active({"id": "a", "name": "X"}) is True


def test_deleted_false() -> None:
    assert is_budget_row_active({"id": "a", "deleted": True}) is False


def test_archived_false() -> None:
    assert is_budget_row_active({"id": "a", "archived": True}) is False


def test_closed_false() -> None:
    assert is_budget_row_active({"id": "a", "closed": True}) is False


def test_active_budgets_only() -> None:
    rows = [
        {"id": "1", "name": "A"},
        {"id": "2", "name": "B", "deleted": True},
    ]
    assert len(active_budgets_only(rows)) == 1
    assert active_budgets_only(rows)[0]["id"] == "1"
