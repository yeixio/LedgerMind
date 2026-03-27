"""JSON API for the local web UI."""

from __future__ import annotations

from datetime import date
from typing import Annotated, Any, cast

from fastapi import APIRouter, Cookie, HTTPException, Request, Response

from ledgermind.api.ynab_client import YNABClient
from ledgermind.config import settings_with_overrides
from ledgermind.domain.types import float_to_milliunits
from ledgermind.exceptions import ConfigurationError, YNABAPIError
from ledgermind.services.forecasting import project_cashflow
from ledgermind.services.snapshot import build_budget_snapshot
from ledgermind.session import month_first_or_today, resolve_budget_id
from ledgermind.web.schemas import SessionCreate, SessionPatch
from ledgermind.web.session_store import SessionStore

SESSION_COOKIE = "lm_sid"
COOKIE_MAX_AGE_SECONDS = 7 * 24 * 3600


def _budget_list_payload(budgets: list[dict[str, Any]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for b in budgets:
        bid = b.get("id")
        if not bid:
            continue
        out.append({"id": str(bid), "name": str(b.get("name", ""))})
    return out


def _find_budget_name(budgets: list[dict[str, Any]], budget_id: str) -> str | None:
    for b in budgets:
        if str(b.get("id", "")) == budget_id:
            return str(b.get("name", "")) or None
    return None


def _validate_budget_id(budgets: list[dict[str, Any]], budget_id: str) -> None:
    ids = {str(b.get("id", "")) for b in budgets if b.get("id")}
    if budget_id not in ids:
        raise HTTPException(status_code=400, detail="Unknown budget id for this token.")


def get_store(request: Request) -> SessionStore:
    return cast(SessionStore, request.app.state.session_store)


def api_router() -> APIRouter:
    r = APIRouter(prefix="/api", tags=["api"])

    @r.post("/session")
    def create_session(
        request: Request,
        response: Response,
        body: SessionCreate,
    ) -> dict[str, Any]:
        token = body.ynab_access_token.strip()
        if not token:
            raise HTTPException(status_code=400, detail="Token is required.")
        try:
            with YNABClient(token) as client:
                budgets = client.list_budgets()
        except YNABAPIError as e:
            raise HTTPException(
                status_code=401,
                detail=f"YNAB rejected this token or request failed: {e}",
            ) from e

        if body.ynab_budget_id:
            _validate_budget_id(budgets, body.ynab_budget_id)

        store = get_store(request)
        sid = store.create(token, body.ynab_budget_id)
        response.set_cookie(
            key=SESSION_COOKIE,
            value=sid,
            httponly=True,
            samesite="lax",
            max_age=COOKIE_MAX_AGE_SECONDS,
            path="/",
        )
        return {
            "ok": True,
            "budgets": _budget_list_payload(budgets),
        }

    @r.patch("/session")
    def patch_session(
        request: Request,
        body: SessionPatch,
        lm_sid: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None,
    ) -> dict[str, Any]:
        if not lm_sid:
            raise HTTPException(status_code=401, detail="Not authenticated.")
        store = get_store(request)
        raw = store.get(lm_sid)
        if not raw:
            raise HTTPException(status_code=401, detail="Session expired.")
        try:
            with YNABClient(raw.ynab_access_token) as client:
                budgets = client.list_budgets()
        except YNABAPIError as e:
            raise HTTPException(status_code=401, detail=str(e)) from e
        _validate_budget_id(budgets, body.ynab_budget_id)
        if not store.update_budget(lm_sid, body.ynab_budget_id):
            raise HTTPException(status_code=401, detail="Session expired.")
        return {"ok": True, "ynab_budget_id": body.ynab_budget_id}

    @r.delete("/session")
    def delete_session(
        request: Request,
        response: Response,
        lm_sid: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None,
    ) -> dict[str, bool]:
        store = get_store(request)
        if lm_sid:
            store.delete(lm_sid)
        response.delete_cookie(SESSION_COOKIE, path="/")
        return {"ok": True}

    @r.get("/me")
    def me(
        request: Request,
        lm_sid: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None,
    ) -> dict[str, Any]:
        if not lm_sid:
            return {"authenticated": False}
        store = get_store(request)
        raw = store.get(lm_sid)
        if not raw:
            return {"authenticated": False}
        try:
            with YNABClient(raw.ynab_access_token) as client:
                settings = settings_with_overrides(
                    ynab_access_token=raw.ynab_access_token,
                    ynab_budget_id=raw.ynab_budget_id,
                )
                budget_id = resolve_budget_id(settings, client)
                budgets = client.list_budgets()
                name = _find_budget_name(budgets, budget_id)
        except (YNABAPIError, ConfigurationError):
            return {"authenticated": True, "valid": False}
        return {
            "authenticated": True,
            "valid": True,
            "ynab_budget_id": budget_id,
            "budget_name": name,
        }

    @r.get("/budgets")
    def list_budgets_api(
        request: Request,
        lm_sid: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None,
    ) -> dict[str, Any]:
        if not lm_sid:
            raise HTTPException(status_code=401, detail="Not authenticated.")
        store = get_store(request)
        raw = store.get(lm_sid)
        if not raw:
            raise HTTPException(status_code=401, detail="Session expired.")
        try:
            with YNABClient(raw.ynab_access_token) as client:
                budgets = client.list_budgets()
        except YNABAPIError as e:
            raise HTTPException(status_code=401, detail=str(e)) from e
        return {"budgets": _budget_list_payload(budgets)}

    @r.get("/snapshot")
    def snapshot_api(
        request: Request,
        month: str | None = None,
        lm_sid: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None,
    ) -> dict[str, Any]:
        if not lm_sid:
            raise HTTPException(status_code=401, detail="Not authenticated.")
        store = get_store(request)
        raw = store.get(lm_sid)
        if not raw:
            raise HTTPException(status_code=401, detail="Session expired.")
        try:
            as_of_d = month_first_or_today(month) if month else date.today()
        except ValueError as e:
            raise HTTPException(status_code=400, detail="Use month=YYYY-MM") from e

        settings = settings_with_overrides(
            ynab_access_token=raw.ynab_access_token,
            ynab_budget_id=raw.ynab_budget_id,
        )
        try:
            with YNABClient(raw.ynab_access_token) as client:
                budget_id = resolve_budget_id(settings, client)
                snap = build_budget_snapshot(client, budget_id, as_of=as_of_d)
        except (YNABAPIError, ConfigurationError) as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        return snap.model_dump(mode="json")

    @r.get("/cashflow")
    def cashflow_api(
        request: Request,
        months: int = 6,
        lm_sid: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None,
    ) -> dict[str, Any]:
        if not lm_sid:
            raise HTTPException(status_code=401, detail="Not authenticated.")
        store = get_store(request)
        raw = store.get(lm_sid)
        if not raw:
            raise HTTPException(status_code=401, detail="Session expired.")
        settings = settings_with_overrides(
            ynab_access_token=raw.ynab_access_token,
            ynab_budget_id=raw.ynab_budget_id,
        )
        buf = settings.ledgermind_minimum_buffer
        buf_m = float_to_milliunits(float(buf))
        try:
            with YNABClient(raw.ynab_access_token) as client:
                bid = resolve_budget_id(settings, client)
                data = project_cashflow(
                    client,
                    bid,
                    months=max(1, min(months, 36)),
                    minimum_buffer_milliunits=buf_m,
                    lookback_months=settings.ledgermind_default_lookback_months,
                )
        except (YNABAPIError, ConfigurationError) as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        return data

    return r
