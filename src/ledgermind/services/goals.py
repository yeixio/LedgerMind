"""Savings goal projections (model, not a guarantee)."""

from __future__ import annotations

import math
from datetime import date
from typing import Any


def project_savings_goal(
    *,
    target_amount_milliunits: int,
    monthly_contribution_milliunits: int,
    current_saved_milliunits: int = 0,
    target_date: str | None = None,
) -> dict[str, Any]:
    """
    Estimate months to goal at a flat contribution, and required contribution for a target date.
    """
    remaining = max(0, target_amount_milliunits - current_saved_milliunits)
    warnings: list[str] = []
    if monthly_contribution_milliunits <= 0:
        warnings.append("monthly_contribution must be > 0 for timeline projection.")
        months_at_rate = None
    else:
        months_at_rate = int(math.ceil(remaining / monthly_contribution_milliunits))

    projected_completion: str | None = None
    if months_at_rate is not None and months_at_rate >= 0:
        y, m = date.today().year, date.today().month
        for _ in range(months_at_rate):
            m += 1
            if m > 12:
                m = 1
                y += 1
        projected_completion = date(y, m, 1).isoformat()

    contribution_for_target: int | None = None
    gap_notes: list[str] = []
    if target_date:
        try:
            parts = target_date.strip().split("-")
            y, mo = int(parts[0]), int(parts[1])
            td = date(y, mo, 1)
        except (ValueError, IndexError):
            td = None
            warnings.append("target_date must be YYYY-MM or YYYY-MM-DD.")
        if td is not None:
            today = date.today().replace(day=1)
            months_left = (td.year - today.year) * 12 + (td.month - today.month)
            if months_left <= 0:
                warnings.append("target_date is not in the future; gap analysis skipped.")
            elif remaining > 0:
                contribution_for_target = int(math.ceil(remaining / months_left))
                if monthly_contribution_milliunits > 0:
                    gap = contribution_for_target - monthly_contribution_milliunits
                    if gap > 0:
                        gap_notes.append(
                            f"Need about {gap / 1000:.2f} more per month than current contribution "
                            f"to hit target date.",
                        )
                    elif gap < 0:
                        gap_notes.append(
                            "Current contribution pace may reach the goal before target_date.",
                        )

    return {
        "target_amount_milliunits": target_amount_milliunits,
        "current_saved_milliunits": current_saved_milliunits,
        "remaining_milliunits": remaining,
        "monthly_contribution_milliunits": monthly_contribution_milliunits,
        "months_to_target_at_current_contribution": months_at_rate,
        "projected_completion_month": projected_completion,
        "contribution_needed_milliunits_for_target_date": contribution_for_target,
        "gap_analysis": gap_notes,
        "warnings": warnings,
        "assumptions": [
            "Flat contribution every month, no return/yield modeled.",
            "Does not account for emergencies or income changes.",
        ],
    }


def stress_scenarios(
    *,
    target_amount_milliunits: int,
    monthly_contribution_milliunits: int,
    current_saved_milliunits: int = 0,
) -> dict[str, Any]:
    """Simple best/base/stress by scaling contribution."""
    base = project_savings_goal(
        target_amount_milliunits=target_amount_milliunits,
        monthly_contribution_milliunits=monthly_contribution_milliunits,
        current_saved_milliunits=current_saved_milliunits,
    )
    best = project_savings_goal(
        target_amount_milliunits=target_amount_milliunits,
        monthly_contribution_milliunits=int(monthly_contribution_milliunits * 1.15),
        current_saved_milliunits=current_saved_milliunits,
    )
    stress = project_savings_goal(
        target_amount_milliunits=target_amount_milliunits,
        monthly_contribution_milliunits=max(1, int(monthly_contribution_milliunits * 0.85)),
        current_saved_milliunits=current_saved_milliunits,
    )
    keys = ("months_to_target_at_current_contribution", "projected_completion_month")
    return {
        "base": {k: base[k] for k in keys},
        "best_plus_15pct_contribution": {k: best[k] for k in keys},
        "stress_minus_15pct_contribution": {k: stress[k] for k in keys},
        "assumptions": base["assumptions"],
    }
