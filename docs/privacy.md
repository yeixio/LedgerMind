# Privacy

LedgerMind is designed to run **on your machine** with **no hosted backend required**.

## What leaves your machine

- **YNAB API**: HTTPS calls to YNAB using your token. No other financial data is sent by default.
- **MCP server**: Tools run in **your** process (e.g. `ledgermind run-mcp`). Data flows to the MCP **client** you configure (e.g. ChatGPT Desktop)—same machine in typical setups. LedgerMind does not add a separate cloud backend.

## Local web UI (`ledgermind serve`)

- The app listens on **`127.0.0.1`** by default (loopback only). Use `--host` / `--port` if you need different bindings.
- You may paste your **personal access token** in the browser; it is sent to the **local** LedgerMind process over HTTP on that interface. **No LedgerMind-hosted server** receives or stores it.
- **MVP storage:** the token is kept in **server memory** (session store) and an **HttpOnly** cookie holds an opaque session id; **not** plain `localStorage`. Stopping the server clears the session unless you add a future keychain option ([mvp_ui_plan.md](planning/mvp_ui_plan.md)).
- Anyone who can use the browser on the same machine while the server runs may access the UI; treat that like access to your CLI session.

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
| Token | Env / `.env` and/or **web UI session** (local server memory); not printed by default logging |
| Log level | Default not `DEBUG`; debug logging only with explicit opt-in |
| MCP | Read-only tools only; no YNAB write endpoints in V1 |
