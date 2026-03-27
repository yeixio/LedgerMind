# Architecture

```text
YNAB API (read-only)
    -> YNABClient (httpx)
    -> normalization -> domain models
    -> services (snapshot, spending, debt, forecasting, …)
    -> CLI  |  MCP (run-mcp)  |  accountant skill (prompting / workflows)
```

- **Money**: YNAB amounts are **milliunits** (1/1000 of the currency unit); domain code uses `int` milliunits unless noted.
- **Secrets**: `YNAB_ACCESS_TOKEN` from the environment (or `.env` for local dev only). Never committed or logged.
- **Caching**: Optional SQLite cache (off by default); see [privacy](privacy.md) and [cache](cache.md).
