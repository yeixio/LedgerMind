"""Optional local YAML for APR and minimum payments (see examples/sample-configs)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from ledgermind.domain.types import float_to_milliunits


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


@dataclass(frozen=True)
class DebtAccountMeta:
    """Per-account overrides for debt simulation."""

    apr_annual_pct: float
    minimum_payment_milliunits: int


def _parse_entry(raw: dict[str, Any]) -> DebtAccountMeta:
    apr = float(raw.get("apr", 0.0))
    min_pay = raw.get("minimum_payment", raw.get("minimumPayment"))
    if min_pay is None:
        min_pay_m = 0
    elif isinstance(min_pay, (int, float)):
        # File amounts are in currency units (e.g. USD dollars)
        min_pay_m = float_to_milliunits(float(min_pay))
    else:
        min_pay_m = 0
    return DebtAccountMeta(apr_annual_pct=apr, minimum_payment_milliunits=min_pay_m)


def load_debt_metadata(path: Path | None) -> dict[str, DebtAccountMeta]:
    """Load debt metadata keyed by slug(account_name) and by raw account id."""
    out: dict[str, DebtAccountMeta] = {}
    if path is None or not path.is_file():
        return out
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    accounts = data.get("accounts", {}) or {}
    for key, val in accounts.items():
        if isinstance(val, dict):
            out[_slug(str(key))] = _parse_entry(val)
    by_id = data.get("by_id", data.get("byId", {})) or {}
    if isinstance(by_id, dict):
        for aid, val in by_id.items():
            if isinstance(val, dict):
                out[str(aid)] = _parse_entry(val)
    return out


def lookup_debt_meta(
    account_id: str,
    account_name: str,
    meta: dict[str, DebtAccountMeta],
) -> DebtAccountMeta | None:
    """Resolve metadata by account id first, then slug(name)."""
    if account_id in meta:
        return meta[account_id]
    return meta.get(_slug(account_name))
