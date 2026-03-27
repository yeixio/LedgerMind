# LedgerMind

LedgerMind is a **privacy-first**, **read-only** assistant for [YNAB](https://www.ynab.com/). It helps you think through debt payoff, savings goals, cash flow, and budget tradeoffs with **transparent assumptions**—not as a CPA, tax advisor, or investment fiduciary.

**License:** see [LICENSE](LICENSE). Personal and non-commercial use is free; commercial entities need a separate agreement.

## Why LedgerMind

- **Local-first**: run on your machine; no hosted backend required for self-use.
- **Read-only (V1)**: no YNAB mutations—no moving money, editing transactions, or changing categories.
- **Composable**: CLI, **local web UI** (`ledgermind serve`), **MCP** for agents, optional **accountant skill** ([docs/skills.md](docs/skills.md)).

## Features (V1 foundation)

- Authenticate with a YNAB **personal access token**
- List budgets; pick default, explicit `YNAB_BUDGET_ID`, or first budget
- **Snapshot**: cash on budget, assigned/available totals, overspent category count, debt accounts on the books
- **Analysis:** debt listing + payoff simulation (with optional local APR/min YAML), savings goal projection, cash-flow projection from recent months, category spending / overspending, subscription-style heuristics
- **MCP:** `ledgermind run-mcp` exposes read-only tools ([docs/mcp-tools.md](docs/mcp-tools.md)); **Skill:** [src/ledgermind/skills/accountant_skill/SKILL.md](src/ledgermind/skills/accountant_skill/SKILL.md)
- Structured domain models with **milliunits** (YNAB’s 1/1000 currency integer)

## Architecture

```text
YNAB API → YNABClient → normalization → services → CLI / web UI / MCP / skill
```

Details: [docs/architecture.md](docs/architecture.md).

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# Add YNAB_ACCESS_TOKEN (https://app.ynab.com/settings/developer)

ledgermind doctor
ledgermind list-budgets
ledgermind snapshot
ledgermind debts
ledgermind cashflow --months 6
ledgermind goal --target 10000 --monthly 300 --by-month 2027-01
ledgermind run-mcp
```

**Web UI (optional):** `pip install -e ".[api]"` then `ledgermind serve` and open `http://127.0.0.1:8765/` — enter your token in the browser (session stored in server memory only). See [docs/setup.md](docs/setup.md).

More: [docs/setup.md](docs/setup.md).

## Example questions (with MCP + skill, upcoming)

- “How long until I pay off my debt with an extra $150/month?”
- “Can I hit $10k saved by November at my current pace?”
- “What spending categories drifted most vs last month?”

## Privacy

Default posture: **no analytics**, **token from env**, **optional SQLite cache off by default**. See [docs/privacy.md](docs/privacy.md).

## Roadmap and progress

- [docs/roadmap.md](docs/roadmap.md)
- [docs/planning/checklist.md](docs/planning/checklist.md)
- Full brief: [docs/planning/initial_plan.md](docs/planning/initial_plan.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Security

See [SECURITY.md](SECURITY.md).
