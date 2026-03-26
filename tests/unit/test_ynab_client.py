"""YNAB HTTP client tests (mocked)."""

import httpx
import pytest
import respx

from ledgermind.api.ynab_client import YNAB_BASE_URL, YNABClient
from ledgermind.exceptions import YNABAPIError


@respx.mock
def test_list_budgets_success() -> None:
    respx.get(f"{YNAB_BASE_URL}budgets").mock(
        return_value=httpx.Response(
            200,
            json={"data": {"budgets": [{"id": "b1", "name": "Main"}]}},
        ),
    )
    with YNABClient("test-token") as client:
        budgets = client.list_budgets()
    assert len(budgets) == 1
    assert budgets[0]["id"] == "b1"


@respx.mock
def test_api_error_raises() -> None:
    respx.get(f"{YNAB_BASE_URL}budgets").mock(return_value=httpx.Response(401, json={}))
    with YNABClient("bad") as client, pytest.raises(YNABAPIError) as ei:
        client.list_budgets()
    assert ei.value.status_code == 401


@respx.mock
def test_transactions_paginate() -> None:
    page1 = {
        "transactions": [{"id": str(i)} for i in range(1000)],
        "server_knowledge": 1000,
    }
    page2 = {
        "transactions": [{"id": "last"}],
        "server_knowledge": 1001,
    }
    respx.get(f"{YNAB_BASE_URL}budgets/b1/transactions").mock(
        side_effect=[
            httpx.Response(200, json={"data": page1}),
            httpx.Response(200, json={"data": page2}),
        ],
    )
    with YNABClient("t") as client:
        txs = client.list_transactions("b1")
    assert len(txs) == 1001
