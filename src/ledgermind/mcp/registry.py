"""V1 MCP tool registry: canonical names and handler wiring."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from ledgermind.mcp import handlers as h

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP

# (public tool name, handler). Names must match docs/mcp-tools.md and the implementation brief.
V1_TOOL_SPECS: list[tuple[str, Callable[..., Any]]] = [
    ("get_budget_snapshot", h.get_budget_snapshot),
    ("get_category_balances", h.get_category_balances),
    ("get_recent_transactions", h.get_recent_transactions),
    ("get_spending_by_category", h.get_spending_by_category),
    ("find_overspending", h.find_overspending),
    ("get_debts", h.get_debts),
    ("simulate_debt_payoff", h.simulate_debt_payoff_tool),
    ("project_savings_goal", h.project_savings_goal_tool),
    ("project_cashflow", h.project_cashflow_tool),
    ("find_subscription_creep", h.find_subscription_creep_tool),
]

V1_TOOL_NAMES: tuple[str, ...] = tuple(name for name, _ in V1_TOOL_SPECS)


def register_v1_tools(mcp: FastMCP) -> None:
    """Register all V1 tools on a FastMCP instance."""
    for name, fn in V1_TOOL_SPECS:
        mcp.add_tool(fn, name=name)
