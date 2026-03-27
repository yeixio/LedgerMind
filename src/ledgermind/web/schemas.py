"""Pydantic models for the local web API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    ynab_access_token: str = Field(min_length=1)
    ynab_budget_id: str | None = None


class SessionPatch(BaseModel):
    ynab_budget_id: str = Field(min_length=1)
