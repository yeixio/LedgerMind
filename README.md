# LedgerMind

LedgerMind is a **privacy-first**, **read-only** assistant for [YNAB](https://www.ynab.com/). It helps you think through debt payoff, savings goals, cash flow, and budget tradeoffs with **transparent assumptions**—not as a CPA, tax advisor, or investment fiduciary.

**License:** see [LICENSE](LICENSE). Personal and non-commercial use is free; commercial entities need a separate agreement.

## Requirements

- **Python 3.12+**
- A YNAB [personal access token](https://app.ynab.com/settings/developer) (for CLI/MCP/env-based use, or entered in the **local web UI**)

## Why LedgerMind

- **Local-first**: run on your machine; no hosted backend required for self-use.
- **Read-only (V1)**: no YNAB mutations—no moving money, editing transactions, or changing categories.
- **Composable**: **CLI**, **local web UI** (`ledgermind serve`), **MCP** for agents, optional **accountant skill** ([docs/skills.md](docs/skills.md)).

## Features (V1 foundation)

- Authenticate with a YNAB **personal access token** (environment / `.env`, or **in-browser** for the web UI—session kept in server memory)
- List budgets; pick default, explicit `YNAB_BUDGET_ID`, or first budget
- **Snapshot**: cash on budget, assigned/available totals, overspent category count, debt accounts on the books
- **Analysis:** debt listing + payoff simulation (with optional local APR/min YAML), savings goal projection, cash-flow projection from recent months, category spending / overspending, subscription-style heuristics
- **Web UI:** `ledgermind serve` — loopback dashboard (snapshot + cash-flow JSON); see [docs/setup.md](docs/setup.md#local-web-ui)
- **MCP:** `ledgermind run-mcp` exposes read-only tools ([docs/mcp-tools.md](docs/mcp-tools.md)); **Skill:** [src/ledgermind/skills/accountant_skill/SKILL.md](src/ledgermind/skills/accountant_skill/SKILL.md)
- Structured domain models with **milliunits** (YNAB’s 1/1000 currency integer)

## Architecture

```text
YNAB API → YNABClient → normalization → services → CLI / web UI / MCP / skill
```

Details: [docs/architecture.md](docs/architecture.md).

## Quickstart (users)

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
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

**Web UI:** install FastAPI extras, then start the server and open the URL (token can be pasted in the UI—no `.env` required for that path):

```bash
pip install -e ".[api]"
ledgermind serve
# http://127.0.0.1:8765/
```

Full install options, Docker, and MCP wiring: [docs/setup.md](docs/setup.md).

## Development

The repo includes a **Makefile** for common tasks on **macOS/Linux** (and Git Bash/WSL on Windows). The default target prints usage:

```bash
make help
```

Typical first-time setup for contributors:

```bash
make install-all    # creates .venv if needed; pip install -e ".[all]"
# optional: pre-commit install
make check          # ruff + mypy + pytest
```

**Web UI in one shot:** `make dev` runs `install-all` and then starts **`ledgermind serve`** — the **REST API and the browser UI are the same process** (FastAPI + static files on `http://127.0.0.1:8765/`). After dependencies are installed once, use **`make serve`** to skip reinstall and start faster.

Useful targets include **`venv`**, **`install`** (`[dev]` only), **`install-api`** (runtime + web extras), **`test`**, **`lint`**, **`typecheck`**, **`docs`** / **`docs-build`**, **`serve`**, **`dev`**, **`precommit`**, and **`clean`**. See the **comment block at the top of [Makefile](Makefile)** for behavior, paths, and platform notes.

**Optional dependency groups** (see [`pyproject.toml`](pyproject.toml)):

| Extra | Purpose |
|-------|---------|
| `[dev]` | Tests (pytest, respx), Ruff, mypy, pre-commit, MkDocs, FastAPI/uvicorn (for web tests) |
| `[api]` | FastAPI + uvicorn for `ledgermind serve` and the web stack |
| `[all]` | `[dev]` + `[api]` — recommended for full local development |

## Example questions (with MCP + skill)

- “How long until I pay off my debt with an extra $150/month?”
- “Can I hit $10k saved by November at my current pace?”
- “What spending categories drifted most vs last month?”

## Privacy

**No analytics** by default. Tokens come from **environment / `.env`** (CLI/MCP) or from the **local web UI** session (in-memory on your machine only). **Optional SQLite cache** is off unless enabled. Details: [docs/privacy.md](docs/privacy.md).

## Roadmap and progress

- [docs/roadmap.md](docs/roadmap.md)
- [docs/planning/checklist.md](docs/planning/checklist.md)
- Full brief: [docs/planning/initial_plan.md](docs/planning/initial_plan.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Security

See [SECURITY.md](SECURITY.md).
