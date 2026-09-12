from __future__ import annotations

import sqlite3

import pytest

from faria_household_mcp.database import HouseholdDatabase
from faria_household_mcp.monitoring import MonitoringService


@pytest.fixture
def database(tmp_path) -> HouseholdDatabase:
    database = HouseholdDatabase(tmp_path / "faria.db")
    database.initialize()
    return database


def test_active_personas_initialize_idle_without_fake_inactive_state(database) -> None:
    states = MonitoringService(database).get_active_persona_states()

    assert [(state.persona, state.status) for state in states] == [
        ("FINANCE", "IDLE"),
        ("GIVING", "IDLE"),
        ("HOME_OPS", "IDLE"),
    ]


def test_working_to_idle_success_transition_is_atomic(database) -> None:
    timestamps = iter(("2099-01-01T00:00:00Z", "2099-01-01T00:01:00Z"))
    monitoring = MonitoringService(database, clock=lambda: next(timestamps))

    monitoring.mark_working("FINANCE", "Monthly allocation confirmation")
    working = monitoring.get_active_persona_states()[0]
    activity = monitoring.record_success(
        "FINANCE",
        "MONTHLY_ALLOCATION_CONFIRMED",
        "Monthly allocation confirmed for 2099-01.",
        "MONTHLY_ALLOCATION",
        "synthetic-reference",
    )
    idle = monitoring.get_active_persona_states()[0]

    assert working.status == "WORKING"
    assert working.current_task == "Monthly allocation confirmation"
    assert activity.status == "SUCCEEDED"
    assert idle.status == "IDLE"
    assert idle.current_task is None
    assert idle.last_activity_at == "2099-01-01T00:01:00Z"
    assert idle.last_error_summary is None


def test_failure_sets_error_without_storing_business_error_details(database) -> None:
    monitoring = MonitoringService(database, clock=lambda: "2099-01-01T00:00:00Z")
    monitoring.mark_working("GIVING", "Giving record creation")

    monitoring.record_failure(
        "GIVING",
        "GIVING_RECORDED",
        "Giving record creation failed.",
    )
    state = monitoring.get_active_persona_states()[1]

    assert state.status == "ERROR"
    assert state.current_task is None
    assert state.last_error_summary == "Giving record creation failed."


def test_activities_are_append_only_and_cannot_mutate_financial_state(database) -> None:
    monitoring = MonitoringService(database, clock=lambda: "2099-01-01T00:00:00Z")
    activity = monitoring.record_success(
        "FINANCE", "SAVINGS_GOAL_CREATED", "Savings goal created."
    )

    with database.connect() as connection:
        assert connection.execute("SELECT COUNT(*) FROM savings_goals").fetchone()[0] == 0
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            connection.execute(
                "UPDATE agent_activities SET summary = 'changed' WHERE id = ?",
                (activity.activity_id,),
            )
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            connection.execute(
                "DELETE FROM agent_activities WHERE id = ?",
                (activity.activity_id,),
            )


def test_recent_activities_are_newest_first_and_bounded(database) -> None:
    timestamps = iter(
        (
            "2099-01-01T00:00:00Z",
            "2099-01-01T00:01:00Z",
            "2099-01-01T00:02:00Z",
        )
    )
    monitoring = MonitoringService(database, clock=lambda: next(timestamps))
    for index in range(3):
        monitoring.record_success("FINANCE", f"ACTIVITY_{index}", f"Activity {index}.")

    recent = monitoring.list_recent(2)

    assert [activity.activity_type for activity in recent] == ["ACTIVITY_2", "ACTIVITY_1"]
