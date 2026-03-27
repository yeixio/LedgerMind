"""Savings goal projection."""

from ledgermind.services.goals import project_savings_goal


def test_goal_timeline() -> None:
    out = project_savings_goal(
        target_amount_milliunits=12_000_000,
        monthly_contribution_milliunits=100_000,
        current_saved_milliunits=0,
    )
    assert out["months_to_target_at_current_contribution"] == 120


def test_goal_target_date_gap() -> None:
    out = project_savings_goal(
        target_amount_milliunits=10_000_000,
        monthly_contribution_milliunits=50_000,
        current_saved_milliunits=0,
        target_date="2030-01",
    )
    assert out["contribution_needed_milliunits_for_target_date"] is not None
    assert out["contribution_needed_milliunits_for_target_date"] > 0
