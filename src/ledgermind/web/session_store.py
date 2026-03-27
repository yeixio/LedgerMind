"""In-memory session storage for the local web UI (credentials in RAM only)."""

from __future__ import annotations

import secrets
import threading
from dataclasses import dataclass


@dataclass
class WebUserSession:
    """YNAB credentials for one browser session."""

    ynab_access_token: str
    ynab_budget_id: str | None


class SessionStore:
    """Thread-safe opaque session id -> credentials."""

    def __init__(self) -> None:
        self._data: dict[str, WebUserSession] = {}
        self._lock = threading.Lock()

    def create(self, token: str, budget_id: str | None) -> str:
        sid = secrets.token_urlsafe(32)
        with self._lock:
            self._data[sid] = WebUserSession(
                ynab_access_token=token,
                ynab_budget_id=budget_id,
            )
        return sid

    def get(self, session_id: str) -> WebUserSession | None:
        with self._lock:
            return self._data.get(session_id)

    def update_budget(self, session_id: str, budget_id: str | None) -> bool:
        with self._lock:
            cur = self._data.get(session_id)
            if cur is None:
                return False
            self._data[session_id] = WebUserSession(
                ynab_access_token=cur.ynab_access_token,
                ynab_budget_id=budget_id,
            )
            return True

    def delete(self, session_id: str) -> None:
        with self._lock:
            self._data.pop(session_id, None)
