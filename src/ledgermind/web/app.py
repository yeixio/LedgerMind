"""FastAPI application for the local web UI."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from ledgermind import __version__
from ledgermind.web.routes_api import api_router
from ledgermind.web.session_store import SessionStore

_STATIC_DIR = Path(__file__).resolve().parent / "static"


def create_app() -> FastAPI:
    app = FastAPI(
        title="LedgerMind",
        version=__version__,
        description="Local read-only YNAB planning UI (loopback only).",
    )
    app.state.session_store = SessionStore()
    app.include_router(api_router())

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(_STATIC_DIR / "index.html")

    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

    return app
