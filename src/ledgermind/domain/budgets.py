"""YNAB budget list helpers (archived / deleted budgets)."""

from __future__ import annotations

from typing import Any


def is_budget_row_active(raw: dict[str, Any]) -> bool:
    """
    True if this budget from GET /budgets should be selectable.

    YNAB may include archived or deleted budgets in the list; those often lack
    current month data. Field names vary; treat missing flags as active.
    """
    inactive = any(
        (
            raw.get("deleted") is True,
            raw.get("Deleted") is True,
            raw.get("archived") is True,
            raw.get("Archived") is True,
            raw.get("closed") is True,
            raw.get("Closed") is True,
        ),
    )
    return not inactive


def active_budgets_only(budgets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Filter to budgets that are not deleted/archived."""
    return [b for b in budgets if is_budget_row_active(b)]
