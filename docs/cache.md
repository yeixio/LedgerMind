# Cache (optional SQLite)

## Current behavior (V1)

- **Default:** caching is **off** (`LEDGERMIND_CACHE_ENABLED=false`).
- **`ledgermind clear-cache`:** removes the cache file path if caching was enabled and the file exists; otherwise reports that nothing was cleared or cache is disabled.

No persistent cache schema is written by core V1 flows until a future implementation lands.

## Intended design (when implemented)

Aligned with the [implementation brief](planning/initial_plan.md):

- **Purpose:** Optional persistence for derived metrics or last-fetched snapshots to reduce YNAB API calls.
- **Location:** Configurable via `LEDGERMIND_CACHE_PATH` (default under user cache dir).
- **Contents (to document per release):** only fields required for the feature; no raw transaction dumps by default.
- **Disable:** set `LEDGERMIND_CACHE_ENABLED=false` or delete the file and use `clear-cache`.

## Privacy

See [privacy](privacy.md). Treat the cache file as **sensitive** if it contains budget-derived data.
