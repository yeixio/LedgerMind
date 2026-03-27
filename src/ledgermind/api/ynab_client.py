"""Read-only YNAB REST client (personal access token)."""

from __future__ import annotations

import logging
import time
from datetime import date
from typing import Any

import httpx

from ledgermind.exceptions import YNABAPIError

_LOG = logging.getLogger(__name__)

YNAB_BASE_URL = "https://api.youneedabudget.com/v1/"
_MAX_TX_PAGE = 1000
_MAX_RETRIES = 3


class YNABClient:
    """Sync HTTP client for YNAB v1. Does not log tokens or Authorization values."""

    def __init__(self, access_token: str, *, timeout: float = 60.0) -> None:
        self._http = httpx.Client(
            base_url=YNAB_BASE_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=timeout,
        )

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> YNABClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        rate_attempts = 0
        while True:
            try:
                resp = self._http.request(method, path.lstrip("/"), params=params)
            except httpx.RequestError as e:
                raise YNABAPIError(f"YNAB request failed: {e}") from e

            if resp.status_code == 429:
                rate_attempts += 1
                if rate_attempts > _MAX_RETRIES:
                    raise YNABAPIError(
                        "YNAB rate limited after retries",
                        status_code=429,
                        body=resp.text[:500],
                    )
                wait = float(resp.headers.get("Retry-After", "2"))
                _LOG.warning("YNAB rate limited; sleeping %.1fs", wait)
                time.sleep(wait)
                continue

            if resp.status_code >= 400:
                raise YNABAPIError(
                    f"YNAB API error {resp.status_code} for {path}",
                    status_code=resp.status_code,
                    body=resp.text[:2000],
                )

            payload = resp.json()
            data = payload.get("data")
            if not isinstance(data, dict):
                raise YNABAPIError("YNAB response missing data object", body=resp.text[:500])
            return data

    def read_budgets_root(self) -> dict[str, Any]:
        """Raw `data` object from GET /budgets (budgets list + default_budget)."""
        return self._request("GET", "budgets")

    def list_budgets(self) -> list[dict[str, Any]]:
        data = self.read_budgets_root()
        budgets = data.get("budgets", [])
        if not isinstance(budgets, list):
            return []
        return budgets

    def default_budget_id(self) -> str | None:
        data = self.read_budgets_root()
        db = data.get("default_budget")
        if isinstance(db, dict):
            bid = db.get("id")
            return str(bid) if bid else None
        return None

    def get_budget(self, budget_id: str) -> dict[str, Any]:
        data = self._request("GET", f"budgets/{budget_id}")
        budget = data.get("budget")
        if not isinstance(budget, dict):
            raise YNABAPIError("budget payload missing")
        return budget

    def list_accounts(self, budget_id: str) -> list[dict[str, Any]]:
        data = self._request("GET", f"budgets/{budget_id}/accounts")
        accounts = data.get("accounts", [])
        return accounts if isinstance(accounts, list) else []

    def list_category_groups(self, budget_id: str) -> list[dict[str, Any]]:
        data = self._request("GET", f"budgets/{budget_id}/categories")
        groups = data.get("category_groups", [])
        return groups if isinstance(groups, list) else []

    def list_payees(self, budget_id: str) -> list[dict[str, Any]]:
        data = self._request("GET", f"budgets/{budget_id}/payees")
        payees = data.get("payees", [])
        return payees if isinstance(payees, list) else []

    def get_month(self, budget_id: str, month: date) -> dict[str, Any]:
        month_id = month.strftime("%Y-%m-01")
        data = self._request("GET", f"budgets/{budget_id}/months/{month_id}")
        m = data.get("month")
        if not isinstance(m, dict):
            raise YNABAPIError("month payload missing")
        return m

    def list_transactions(
        self,
        budget_id: str,
        *,
        since_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch all transactions, paging with last_knowledge_of_server when needed."""
        params: dict[str, Any] = {}
        if since_date is not None:
            params["since_date"] = since_date.isoformat()

        out: list[dict[str, Any]] = []
        last_knowledge: int | None = None
        previous_knowledge: int | None = None

        while True:
            page_params = dict(params)
            if last_knowledge is not None:
                page_params["last_knowledge_of_server"] = last_knowledge

            data = self._request("GET", f"budgets/{budget_id}/transactions", params=page_params)
            batch = data.get("transactions", [])
            if not isinstance(batch, list):
                break
            out.extend(batch)

            sk = data.get("server_knowledge")
            if not isinstance(sk, int):
                break
            if len(batch) < _MAX_TX_PAGE:
                break
            if sk == previous_knowledge:
                _LOG.warning("YNAB transaction pagination stalled; stopping at %s rows", len(out))
                break
            previous_knowledge = sk
            last_knowledge = sk

        return out
