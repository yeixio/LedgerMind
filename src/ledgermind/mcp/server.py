"""MCP stdio server (FastMCP)."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ledgermind.config import load_settings
from ledgermind.logging import setup_logging
from ledgermind.mcp import handlers as h


def create_mcp_app() -> FastMCP:
    """Build FastMCP with all V1 tools registered."""
    mcp = FastMCP(
        "LedgerMind",
        instructions=(
            "Read-only YNAB planning tools. Monetary fields use YNAB milliunits unless noted "
            "(1000 milliunits = 1.00 in the budget currency). This is educational planning "
            "output, not tax, legal, or investment advice."
        ),
    )
    mcp.add_tool(h.get_budget_snapshot)
    mcp.add_tool(h.get_category_balances)
    mcp.add_tool(h.get_recent_transactions)
    mcp.add_tool(h.get_spending_by_category)
    mcp.add_tool(h.find_overspending)
    mcp.add_tool(h.get_debts)
    mcp.add_tool(h.simulate_debt_payoff_tool, name="simulate_debt_payoff")
    mcp.add_tool(h.project_savings_goal_tool, name="project_savings_goal")
    mcp.add_tool(h.project_cashflow_tool, name="project_cashflow")
    mcp.add_tool(h.find_subscription_creep_tool, name="find_subscription_creep")
    return mcp


def run_stdio_server() -> None:
    """Entry point for `ledgermind run-mcp`."""
    settings = load_settings()
    setup_logging(settings.ledgermind_log_level, debug_financial=settings.ledgermind_debug_log)
    create_mcp_app().run(transport="stdio")


def main() -> None:
    run_stdio_server()
