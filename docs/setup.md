# Setup

## Requirements

- Python **3.12+**
- A YNAB [personal access token](https://app.ynab.com/settings/developer)

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

Phase 3: `ledgermind run-mcp` will start the stdio MCP server. Until then the command exits with a notice.
