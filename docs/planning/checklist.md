# LedgerMind build checklist

Track implementation progress against [`initial_plan.md`](initial_plan.md). Check boxes as work completes. Update this file in the same PR as substantive changes when practical.

---

## Principles (ongoing)

- [x] Privacy first: local-first default, no unnecessary third-party data, safe logging defaults
- [x] Read-only first: no YNAB mutations in V1
- [ ] Transparent calculations: assumptions and model-vs-fact labeling (expand with Phase 2+ forecasts)
- [x] Safe financial framing: disclaimers, no regulated-advice posture (README, docs, prompts)
- [x] Quality bar: clean architecture, docs, tests, predictable layout

---

## Repository scaffold

Root and tooling

- [x] `pyproject.toml` (Python 3.12+, httpx, pydantic; FastAPI optional extra `[api]`)
- [x] `README.md` (what, why, features, privacy, architecture, quickstart, examples, roadmap, contrib links)
- [x] `LICENSE` (present)
- [x] `CONTRIBUTING.md`
- [x] `CODE_OF_CONDUCT.md`
- [x] `SECURITY.md`
- [x] `.env.example`
- [x] `Dockerfile` and `docker-compose.yml`
- [x] Ruff, mypy, pre-commit configured
- [x] MkDocs wired for `docs/` (`mkdocs.yml`, `mkdocs` in dev extras)

`src/ledgermind/` layout

- [x] Package `__init__.py`, `config.py`, `logging.py`, `cli.py`
- [x] `api/ynab_client.py`
- [x] `domain/` (`models.py`, `normalization.py`, `types.py`)
- [x] `services/` (`snapshot` implemented; others Phase 2 stubs)
- [x] `mcp/` (`server.py`, `registry.py`, `tools/*` — Phase 3 placeholders)
- [x] `skills/` (`README.md`, `accountant_skill/SKILL.md` — Phase 4 placeholder body)
- [x] `cache/sqlite.py` (clear-cache only until caching lands)
- [x] `tests/unit`, `tests/integration`, `tests/fixtures`
- [x] `examples/` (`prompts.md`, `sample-configs/`, `sample-outputs/`)

---

## MVP scope (V1 in-scope)

- [x] YNAB auth with personal access token
- [x] Read budgets, accounts, categories, payees, transactions (client + transaction pagination)
- [x] Normalize YNAB → LedgerMind domain models (accounts, month, categories; extend in Phase 2)
- [ ] Core MCP tools exposed and documented
- [ ] Debt payoff simulation
- [ ] Savings goal projections
- [ ] Cash-flow trend / projection analysis
- [ ] Category spending summaries
- [x] Clear docs and self-host instructions (initial; deepen in Phase 5)

---

## Phase 1 — Foundation

- [x] Initialize repo and tooling (matches scaffold above)
- [x] Config and settings module (`YNAB_ACCESS_TOKEN`, `YNAB_BUDGET_ID`, optional vars per plan)
- [x] Structured logging with redaction; safe debug mode
- [x] YNAB client: auth, budgets, accounts, categories, payees, transactions, pagination/rate limits, errors
- [x] Core domain models and money handling (units documented)
- [x] CLI: `doctor`, `list-budgets`, `snapshot`, `clear-cache`; `run-mcp` stub (Phase 3)
- [x] README, CONTRIBUTING, SECURITY (Phase 1 deliverable set)

**Phase 1 exit:** project runs locally; authenticates to YNAB; lists budgets; shows a snapshot. **Done.**

---

## Phase 2 — Core analysis services

- [ ] Snapshot service (month available/spending, net cash, summary) — Phase 1 covers basic snapshot; extend per plan
- [ ] Spending service (by category, trends, averages, drift, MoM changes)
- [ ] Debt service (debt-like accounts, metadata file for APR/min payment, avalanche/snowball, payoff date, interest, compare)
- [ ] Goal service (months to target, contribution vs needed, scenarios)
- [ ] Forecasting service (short-term projection, buffer, assumptions in output)
- [ ] Subscription detection (recurring inference, cadence, amount creep)
- [ ] CLI: `snapshot`, `debts`, `cashflow --months`, `goal --target … --monthly …`, `clear-cache`

**Phase 2 exit:** CLI answers core planning questions end-to-end.

---

## Phase 3 — MCP server

- [ ] MCP server skeleton and `run-mcp` entry
- [ ] Tool registry with schemas and docstrings
- [ ] `get_budget_snapshot`
- [ ] `get_category_balances`
- [ ] `get_recent_transactions`
- [ ] `get_spending_by_category`
- [ ] `find_overspending`
- [ ] `get_debts`
- [ ] `simulate_debt_payoff`
- [ ] `project_savings_goal`
- [ ] `project_cashflow`
- [ ] `find_subscription_creep`
- [ ] Structured outputs validated; integration tests for tool shapes

**Phase 3 exit:** ChatGPT-compatible MCP server with read-only V1 tools.

---

## Phase 4 — Skill package

- [ ] `accountant_skill/SKILL.md` (planning behavior, tool usage, workflows)
- [ ] Debt payoff workflow guidance
- [ ] Savings goal workflow guidance
- [ ] Affordability workflow guidance
- [ ] Monthly review workflow guidance
- [ ] Output style: answer first, assumptions, options, risks, next action
- [ ] Example prompts (`examples/prompts.md` and/or skill docs)
- [ ] Limitations and assumptions documented

**Phase 4 exit:** reusable assistant behavior layer documented.

---

## Phase 5 — Polish and release readiness

- [x] Docs pass: `docs/index.md`, `architecture.md`, `setup.md`, `privacy.md`, `mcp-tools.md`, `skills.md`, `roadmap.md`, `examples.md` (initial drafts; deepen later)
- [x] Docker workflow verified and documented
- [x] Sample configs and sample outputs (sample outputs folder placeholder)
- [ ] Roadmap + GitHub issue/PR templates (optional but in plan)
- [ ] Privacy defaults verified (cache off path, logging, no telemetry)

**Phase 5 exit:** strong public release candidate.

---

## Phase 6 — Future (not V1; design only)

- [ ] OAuth / multi-user cloud (future)
- [ ] Optional web UI
- [ ] Write actions with confirmations
- [ ] Richer forecasting, recurring income, multi-budget, plugins

---

## Configuration

- [x] Required: `YNAB_ACCESS_TOKEN`, `YNAB_BUDGET_ID` (or default budget selection)
- [x] Optional: cache enabled/path, minimum buffer, lookback months, log level, debt metadata file path
- [x] Debt metadata YAML documented (local-only, sensitive) — `examples/sample-configs/debt-metadata.example.yaml`
- [x] No secrets in repo; token never logged

---

## Privacy and security

- [x] Default local-first documentation path
- [x] No default analytics
- [ ] Cache: documented fields; disable persistence option; clear-cache command (clear-cache done; SQLite persistence Phase 2+)
- [ ] Data minimization in MCP responses
- [x] `docs/privacy.md` + threat model (local compromise, env exposure, debug logging, broad tool outputs, future writes)
- [x] Disclaimer language in docs and skill (docs + prompts; skill body Phase 4)

---

## Testing

Unit

- [x] Normalization
- [x] Snapshot assembly (basic)
- [ ] Debt payoff math
- [ ] Goal projection math
- [ ] Subscription heuristics
- [ ] Cash-flow forecasting
- [ ] Config loading

Integration

- [x] YNAB client with mocked HTTP (e.g. respx)
- [ ] MCP tool output shape
- [ ] CLI commands

Golden / fixture

- [ ] Debt comparison outputs
- [ ] Monthly review structures
- [ ] Affordability analysis structures

Fixtures: sanitized only; no real financial data.

---

## V1 acceptance criteria

- [ ] Clone → token → running locally in under 15 minutes (documented)
- [ ] CLI: budget snapshot, debt summary, at least one forecast
- [ ] MCP: core read-only tools reliable
- [ ] Docs sufficient for architecture and contribution
- [ ] Privacy defaults strong and documented
- [ ] No YNAB write actions in V1
- [ ] Tests cover core financial calculations
- [ ] Skill package documents intended assistant behavior

---

## Starter issues (optional tracking)

Mirror [`initial_plan.md` suggested issues](initial_plan.md) or GitHub issues: Foundation, Domain, Analysis, MCP, Docs.

---

## Nice-to-have after V1

- [ ] Richer monthly review summaries
- [ ] Better recurring bill detection
- [ ] What-if scenario tables
- [ ] Optional charts
- [ ] Better debt metadata UX
- [ ] Import/export scenario assumptions
- [ ] Multi-user abstraction for future hosting
