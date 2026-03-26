# Privacy

LedgerMind is designed to run **on your machine** with **no hosted backend required**.

## What leaves your machine

- **YNAB API**: HTTPS calls to YNAB using your token. No other financial data is sent by default.
- **Future MCP**: Tools run where you host the MCP server (typically the same machine as ChatGPT Desktop or your client).

## What is stored locally

- Optional **SQLite cache** when `LEDGERMIND_CACHE_ENABLED=true` (default **false**). Document fields when implemented.
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
