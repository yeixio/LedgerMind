"""Shared domain types.

Money in LedgerMind
-------------------
YNAB exposes currency amounts as **milliunits** (1/1000 of the currency unit).
LedgerMind keeps money as ``int`` milliunits in domain models unless noted.
Convert to display units with ``milliunits_to_float(amount)``.
"""

from typing import NewType

# Whole currency amounts in YNAB milliunits (e.g. USD 10.00 -> 10_000).
Milliunits = NewType("Milliunits", int)


def milliunits_to_float(m: int) -> float:
    """Convert YNAB milliunits to a float in currency units (for display only)."""
    return m / 1000.0


def float_to_milliunits(x: float) -> int:
    """Convert currency units to milliunits (rounded)."""
    return int(round(x * 1000))
