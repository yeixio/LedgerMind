"""Local loopback web UI (FastAPI). Optional dependency: pip install -e \".[api]\"."""

from ledgermind.web.app import create_app

__all__ = ["create_app"]
