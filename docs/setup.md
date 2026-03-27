# Setup

## Requirements

- Python **3.12+**
- A YNAB [personal access token](https://app.ynab.com/settings/developer)

## Quick path (under 15 minutes)

From a clean clone: create a venv, `pip install -e ".[dev]"`, copy `.env.example` to `.env`, add `YNAB_ACCESS_TOKEN`, run `ledgermind doctor` then `ledgermind list-budgets` and `ledgermind snapshot`. If anything fails, use `ledgermind doctor` output and [privacy.md](privacy.md) (token handling).

## Local install

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env
# Edit .env: set YNAB_ACCESS_TOKEN and optionally YNAB_BUDGET_ID
```

## CLI

```bash
ledgermind doctor
ledgermind list-budgets
ledgermind snapshot
ledgermind snapshot --month 2025-03
ledgermind debts
ledgermind cashflow --months 6
ledgermind goal --target 5000 --monthly 300
ledgermind run-mcp
```

Point your MCP client at `ledgermind run-mcp` with the same env vars; see [mcp-tools.md](mcp-tools.md).

## Local web UI

Requires the **`[api]`** extra (FastAPI + uvicorn):

```bash
pip install -e ".[api]"
ledgermind serve
# Open http://127.0.0.1:8765/ — bind address and port: --host / --port
```

Enter your **YNAB personal access token** in the UI (not in `.env` required for this path). The server keeps credentials **in memory** for your session; restarting `serve` clears them. See **Local web UI** in [privacy.md](privacy.md).

## Docker

```bash
cp .env.example .env  # add token
docker compose build
docker compose run --rm ledgermind doctor
docker compose run --rm ledgermind snapshot
```

## Docs site (optional)

```bash
pip install -e ".[dev]"
mkdocs serve
```

## MCP server

`ledgermind run-mcp` starts the **stdio** MCP server (FastMCP). Configure your client to launch this command with the same environment variables as the CLI (`YNAB_ACCESS_TOKEN`, optional `YNAB_BUDGET_ID`, etc.). Tool reference: [mcp-tools.md](mcp-tools.md).
