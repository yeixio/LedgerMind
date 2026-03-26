"""Internal domain models (post-normalization)."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Account(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    account_type: str
    on_budget: bool
    closed: bool
    balance_milliunits: int
    cleared_balance_milliunits: int
    uncleared_balance_milliunits: int


class CategoryMonth(BaseModel):
    """Per-category values for a budget month (assigned / activity / available)."""

    model_config = ConfigDict(frozen=True)

    category_id: str
    name: str
    category_group_name: str | None
    assigned_milliunits: int
    activity_milliunits: int
    available_milliunits: int
    hidden: bool = False


class BudgetMonthSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    month: date
    to_be_budgeted_milliunits: int
    age_of_money: int | None = None
    income_milliunits: int = 0
    budgeted_milliunits: int = 0
    activity_milliunits: int = 0


class BudgetSnapshot(BaseModel):
    """High-level snapshot for CLI and future MCP tools."""

    model_config = ConfigDict(frozen=True)

    budget_id: str
    budget_name: str
    as_of: date
    currency_format_iso: str | None = None
    total_cash_on_budget_milliunits: int = Field(
        description="Sum of on-budget cash account balances (milliunits).",
    )
    total_assigned_milliunits: int = Field(
        description="Sum of assigned across categories for the month (milliunits).",
    )
    total_available_milliunits: int = Field(
        description="Sum of available across categories for the month (milliunits).",
    )
    overspent_category_count: int = 0
    to_be_budgeted_milliunits: int = 0
    age_of_money: int | None = None
    debt_accounts: list[Account] = Field(default_factory=list)


AccountTypeDebtLike = Literal[
    "creditCard",
    "lineOfCredit",
    "loan",
    "mortgage",
    "otherLiability",
]
