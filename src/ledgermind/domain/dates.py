"""Budget month date helpers."""

from __future__ import annotations

from datetime import date


def month_starts_ending_at(end_month: date, count: int) -> list[date]:
    """Return `count` month-start dates ending at `end_month` (day ignored), oldest first."""
    y, m = end_month.year, end_month.month
    raw: list[date] = []
    for _ in range(count):
        raw.append(date(y, m, 1))
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    raw.reverse()
    return raw
