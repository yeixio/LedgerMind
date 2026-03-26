"""Domain normalization tests."""

from ledgermind.domain.normalization import normalize_account, normalize_budget_month


def test_normalize_account_camel_case() -> None:
    raw = {
        "id": "a1",
        "name": "Checking",
        "type": "checking",
        "onBudget": True,
        "closed": False,
        "balance": 10_000,
        "clearedBalance": 10_000,
        "unclearedBalance": 0,
    }
    a = normalize_account(raw)
    assert a.name == "Checking"
    assert a.on_budget is True
    assert a.balance_milliunits == 10_000


def test_normalize_budget_month() -> None:
    raw = {
        "month": "2025-03-01",
        "toBeBudgeted": 5000,
        "ageOfMoney": 14,
        "income": 100_000,
        "budgeted": 95_000,
        "activity": -90_000,
    }
    m = normalize_budget_month(raw)
    assert m.to_be_budgeted_milliunits == 5000
    assert m.age_of_money == 14
