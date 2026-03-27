"""Local web API smoke tests (mocked YNAB)."""

from __future__ import annotations

import httpx
import pytest
import respx
from fastapi.testclient import TestClient

from ledgermind.web.app import create_app
from ledgermind.web.routes_api import SESSION_COOKIE

_BUDGETS_JSON = {
    "data": {
        "budgets": [
            {"id": "00000000-0000-4000-8000-000000000001", "name": "Test Budget"},
        ],
    },
}


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_index(client: TestClient) -> None:
    r = client.get("/")
    assert r.status_code == 200
    assert b"LedgerMind" in r.content


@respx.mock
def test_session_and_me(client: TestClient) -> None:
    respx.get("https://api.youneedabudget.com/v1/budgets").mock(
        return_value=httpx.Response(200, json=_BUDGETS_JSON),
    )
    r = client.post(
        "/api/session",
        json={
            "ynab_access_token": "test-token",
            "ynab_budget_id": "00000000-0000-4000-8000-000000000001",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert len(body["budgets"]) == 1
    assert SESSION_COOKIE in r.cookies

    r2 = client.get("/api/me")
    assert r2.status_code == 200
    me = r2.json()
    assert me["authenticated"] is True
    assert me["valid"] is True
    assert me["ynab_budget_id"] == "00000000-0000-4000-8000-000000000001"


def test_budgets_unauthorized(client: TestClient) -> None:
    r = client.get("/api/budgets")
    assert r.status_code == 401


@respx.mock
def test_delete_session(client: TestClient) -> None:
    respx.get("https://api.youneedabudget.com/v1/budgets").mock(
        return_value=httpx.Response(200, json=_BUDGETS_JSON),
    )
    client.post("/api/session", json={"ynab_access_token": "t", "ynab_budget_id": None})
    r2 = client.delete("/api/session")
    assert r2.status_code == 200
    r3 = client.get("/api/me")
    assert r3.json()["authenticated"] is False
