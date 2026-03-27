# Privacy

LedgerMind is designed to run **on your machine** with **no hosted backend required**.

## What leaves your machine

- **YNAB API**: HTTPS calls to YNAB using your token. No other financial data is sent by default.
- **MCP server**: Tools run in **your** process (e.g. `ledgermind run-mcp`). Data flows to the MCP **client** you configure (e.g. ChatGPT Desktop)—same machine in typical setups. LedgerMind does not add a separate cloud backend.

## Data minimization (MCP / tools)

V1 tools return **structured summaries** (totals, capped transaction lists, memo previews). See [mcp-tools.md](mcp-tools.md) for parameters (e.g. `limit` on recent transactions). Prefer the smallest inputs that answer the question; avoid dumping full history when a summary suffices.

## What is stored locally

- Optional **SQLite cache** when `LEDGERMIND_CACHE_ENABLED=true` (default **false**). See [cache.md](cache.md) for behavior and intended design.
- **`.env`** for local configuration (never commit).

## Logging

- Default logging avoids printing tokens and redacts `Authorization` patterns.
- Avoid `LEDGERMIND_DEBUG_LOG=true` unless you understand the risk of verbose logs.

## Threats to consider

- Compromise of your laptop or container
- Leaked environment variables
- Accidentally enabling verbose logging in shared environments
- Over-broad tool responses in future versions (prefer summaries; V1 is read-only)

LedgerMind provides **educational and planning assistance**, not regulated professional advice.

## Verification checklist (release)

Use this when validating a stock install or release candidate:

| Check | Pass criteria |
|-------|----------------|
| No telemetry | No analytics SDKs or third-party reporting in default code paths |
| Cache default | `LEDGERMIND_CACHE_ENABLED` unset or `false`; no cache file required for core flows |
| Token | Only in env / `.env`; not printed by default logging |
| Log level | Default not `DEBUG`; debug logging only with explicit opt-in |
| MCP | Read-only tools only; no YNAB write endpoints in V1 |
