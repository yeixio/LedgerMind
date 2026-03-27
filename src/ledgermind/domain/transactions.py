"""Public transaction shapes for tools (minimize memo PII)."""


from __future__ import annotations

from typing import Any


def _mask_memo(memo: str, keep: int = 4) -> str:
    if len(memo) <= keep:
        return ""
    return memo[:keep] + "…"


def transaction_summary(raw: dict[str, Any]) -> dict[str, Any]:
    memo = raw.get("memo") or raw.get("Memo") or ""
    return {
        "id": str(raw.get("id", "")),
        "date": str(raw.get("date", ""))[:10],
        "payee": raw.get("payee_name") or raw.get("payeeName"),
        "amount_milliunits": int(raw.get("amount", 0)),
        "category_id": raw.get("category_id") or raw.get("categoryId"),
        "memo_preview": _mask_memo(str(memo)) if memo else None,
    }
