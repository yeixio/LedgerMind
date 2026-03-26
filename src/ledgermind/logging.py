"""Structured logging with redaction of secrets and high-risk fields."""

from __future__ import annotations

import logging
import re
from typing import Any

_REDACT_KEYS = frozenset(
    {
        "authorization",
        "ynab_access_token",
        "access_token",
        "token",
        "password",
        "secret",
    }
)

# Bearer tokens in arbitrary log text
_BEARER = re.compile(r"(Bearer\s+)[A-Za-z0-9._\-~+/]+=*", re.IGNORECASE)


def _redact_value(key: str, value: Any) -> Any:
    lk = key.lower().replace("-", "_")
    if lk in _REDACT_KEYS or lk.endswith("_token") or lk.endswith("_secret"):
        return "[REDACTED]"
    if isinstance(value, str) and lk == "memo":
        return _mask_memo(value)
    return value


def _mask_memo(memo: str, keep: int = 4) -> str:
    if len(memo) <= keep:
        return "[REDACTED]"
    return memo[:keep] + "…[REDACTED]"


def redact_headers(headers: dict[str, str]) -> dict[str, str]:
    return {k: str(_redact_value(k, v)) for k, v in headers.items()}


def redact_message(message: str) -> str:
    return _BEARER.sub(r"\1[REDACTED]", message)


class RedactingFormatter(logging.Formatter):
    """Formatter that strips bearer tokens from the final log line."""

    def format(self, record: logging.LogRecord) -> str:
        original = super().format(record)
        return redact_message(original)


def setup_logging(level: str, *, debug_financial: bool = False) -> None:
    """Configure root logging. When debug_financial is False, avoid verbose PII in handlers."""
    root = logging.getLogger()
    root.handlers.clear()
    handler = logging.StreamHandler()
    handler.setFormatter(
        RedactingFormatter("%(levelname)s %(name)s %(message)s"),
    )
    root.addHandler(handler)
    root.setLevel(level.upper())
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    if not debug_financial:
        logging.getLogger("ledgermind").setLevel(level.upper())
