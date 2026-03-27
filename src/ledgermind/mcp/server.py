"""MCP stdio server (FastMCP)."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ledgermind.config import load_settings
from ledgermind.logging import setup_logging
from ledgermind.mcp.registry import register_v1_tools


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
    register_v1_tools(mcp)
    return mcp


def run_stdio_server() -> None:
    """Entry point for `ledgermind run-mcp`."""
    settings = load_settings()
    setup_logging(settings.ledgermind_log_level, debug_financial=settings.ledgermind_debug_log)
    create_mcp_app().run(transport="stdio")


def main() -> None:
    run_stdio_server()
