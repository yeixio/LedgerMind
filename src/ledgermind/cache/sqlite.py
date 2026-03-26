"""SQLite cache (optional). Phase 1: clear path only; persistence arrives with caching feature."""

from __future__ import annotations

from pathlib import Path

from ledgermind.config import Settings


def clear_cache(settings: Settings) -> str:
    """Remove cache file if it exists. Returns a short status message."""
    if not settings.ledgermind_cache_enabled:
        return "Cache is disabled (LEDGERMIND_CACHE_ENABLED=false); nothing to clear."
    path: Path = settings.ledgermind_cache_path
    if not path.exists():
        return f"No cache file at {path}."
    path.unlink()
    return f"Removed cache file {path}."
