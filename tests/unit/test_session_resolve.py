"""Budget id resolution (active vs archived default)."""

from __future__ import annotations

from typing import Any

import pytest

from ledgermind.config import Settings
from ledgermind.exceptions import ConfigurationError
from ledgermind.session import resolve_budget_id, resolve_web_budget_id


class _FakeClient:
    def __init__(self, root: dict[str, Any]) -> None:
        self._root = root

    def read_budgets_root(self) -> dict[str, Any]:
        return self._root


def test_resolve_skips_default_when_archived() -> None:
    settings = Settings(ynab_access_token="t", ynab_budget_id=None)
    root = {
        "budgets": [
            {"id": "archived", "name": "Old", "deleted": True},
            {"id": "active", "name": "Current"},
        ],
        "default_budget": {"id": "archived"},
    }
    assert resolve_budget_id(settings, _FakeClient(root)) == "active"


def test_resolve_uses_default_when_active() -> None:
    settings = Settings(ynab_access_token="t", ynab_budget_id=None)
    root = {
        "budgets": [
            {"id": "a", "name": "A"},
            {"id": "b", "name": "B"},
        ],
        "default_budget": {"id": "b"},
    }
    assert resolve_budget_id(settings, _FakeClient(root)) == "b"


def test_resolve_explicit_overrides() -> None:
    settings = Settings(ynab_access_token="t", ynab_budget_id="a")
    root = {"budgets": [{"id": "a"}, {"id": "b"}], "default_budget": {"id": "b"}}
    assert resolve_budget_id(settings, _FakeClient(root)) == "a"


def test_resolve_web_none_when_multiple_active() -> None:
    settings = Settings(ynab_access_token="t", ynab_budget_id=None)
    root = {
        "budgets": [
            {"id": "a", "name": "A"},
            {"id": "b", "name": "B"},
        ],
        "default_budget": {"id": "a"},
    }
    assert resolve_web_budget_id(settings, _FakeClient(root)) is None


def test_resolve_web_single_active_still_requires_explicit_in_settings() -> None:
    """Web flow always uses the picker; no auto id until ynab_budget_id is set."""
    settings = Settings(ynab_access_token="t", ynab_budget_id=None)
    root = {
        "budgets": [
            {"id": "only", "name": "Only"},
        ],
        "default_budget": {"id": "only"},
    }
    assert resolve_web_budget_id(settings, _FakeClient(root)) is None


def test_resolve_all_inactive_raises() -> None:
    settings = Settings(ynab_access_token="t", ynab_budget_id=None)
    root = {
        "budgets": [
            {"id": "x", "deleted": True},
        ],
        "default_budget": {"id": "x"},
    }
    with pytest.raises(ConfigurationError, match="No active budgets"):
        resolve_budget_id(settings, _FakeClient(root))
