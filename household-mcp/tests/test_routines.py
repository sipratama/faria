from __future__ import annotations

import sqlite3
from datetime import UTC, datetime

import pytest

from faria_household_mcp.database import HouseholdDatabase
from faria_household_mcp.routines import (
    RoutineConflictError,
    RoutineService,
    RoutineValidationError,
)

NOW = datetime(2099, 1, 15, 1, 30, tzinfo=UTC)


@pytest.fixture
def database(tmp_path) -> HouseholdDatabase:
    return HouseholdDatabase(tmp_path / "faria.db")


@pytest.fixture
def service(database) -> RoutineService:
    return RoutineService(database, clock=lambda: NOW)


def test_create_valid_one_off_starts_pending_without_scheduler(service) -> None:
    routine = service.create(
        "Synthetic gallon check",
        "ONE_OFF",
        "2099-01-15T19:00:00+07:00",
        "Asia/Jakarta",
        "Synthetic acceptance reminder.",
    )

    assert routine.status == "PENDING_SCHEDULE"
    assert routine.scheduler_job_id is None
    assert routine.next_due_at is None
    assert routine.schedule_expression == "2099-01-15T19:00:00+07:00"


def test_create_valid_recurring_canonicalizes_five_field_cron(service) -> None:
    routine = service.create(
        "Synthetic internet check",
        "RECURRING",
        "0   9  20 * *",
        "Asia/Jakarta",
    )

    assert routine.status == "PENDING_SCHEDULE"
    assert routine.schedule_expression == "0 9 20 * *"


@pytest.mark.parametrize(
    ("title", "kind", "expression", "timezone", "message"),
    (
        ("", "ONE_OFF", "2099-01-15T19:00:00+07:00", "Asia/Jakarta", "title is required"),
        (
            "Synthetic",
            "DAILY",
            "0 9 * * *",
            "Asia/Jakarta",
            "schedule_kind must be ONE_OFF or RECURRING",
        ),
        (
            "Synthetic",
            "ONE_OFF",
            "2099-01-15T19:00:00",
            "Asia/Jakarta",
            "offset-aware ISO timestamp",
        ),
        (
            "Synthetic",
            "ONE_OFF",
            "2099-01-15T19:00:00+08:00",
            "Asia/Jakarta",
            "Asia/Jakarta offset",
        ),
        (
            "Synthetic",
            "RECURRING",
            "not a cron",
            "Asia/Jakarta",
            "exactly 5 fields",
        ),
        (
            "Synthetic",
            "RECURRING",
            "61 9 * * *",
            "Asia/Jakarta",
            "is invalid",
        ),
        (
            "Synthetic",
            "RECURRING",
            "0 9 * * *",
            "UTC",
            "timezone must be Asia/Jakarta",
        ),
    ),
)
def test_create_rejects_invalid_routine_input(
    service, title, kind, expression, timezone, message
) -> None:
    with pytest.raises(RoutineValidationError, match=message):
        service.create(title, kind, expression, timezone)


def test_scheduler_link_activates_and_same_retry_is_idempotent(service) -> None:
    pending = service.create(
        "Synthetic recurring",
        "RECURRING",
        "0 9 20 * *",
        "Asia/Jakarta",
    )

    active = service.link_scheduler(pending.routine_id, "cron-synthetic-1")
    repeated = service.link_scheduler(pending.routine_id, "cron-synthetic-1")

    assert active.status == "ACTIVE"
    assert active.scheduler_job_id == "cron-synthetic-1"
    assert active.next_due_at == "2099-01-20T09:00:00+07:00"
    assert repeated == active


def test_scheduler_link_rejects_conflicting_or_terminal_transition(service) -> None:
    routine = service.create(
        "Synthetic one-off",
        "ONE_OFF",
        "2099-01-15T19:00:00+07:00",
        "Asia/Jakarta",
    )
    service.link_scheduler(routine.routine_id, "cron-synthetic-1")

    with pytest.raises(RoutineConflictError, match="cannot be scheduler-linked"):
        service.link_scheduler(routine.routine_id, "cron-synthetic-2")

    service.cancel(routine.routine_id)
    with pytest.raises(RoutineConflictError, match="cannot be scheduler-linked"):
        service.link_scheduler(routine.routine_id, "cron-synthetic-1")


def test_scheduler_job_id_cannot_be_shared_between_routines(service) -> None:
    first = service.create(
        "Synthetic first", "RECURRING", "0 9 * * *", "Asia/Jakarta"
    )
    second = service.create(
        "Synthetic second", "RECURRING", "0 10 * * *", "Asia/Jakarta"
    )
    service.link_scheduler(first.routine_id, "cron-shared")

    with pytest.raises(RoutineConflictError, match="already linked"):
        service.link_scheduler(second.routine_id, "cron-shared")


def test_one_off_lifecycle_completes_and_disappears_from_open_list(service) -> None:
    pending = service.create(
        "Synthetic one-off",
        "ONE_OFF",
        "2099-01-15T19:00:00+07:00",
        "Asia/Jakarta",
    )
    active = service.link_scheduler(pending.routine_id, "cron-one-off")
    completed = service.complete(active.routine_id)

    assert completed.status == "COMPLETED"
    assert completed.last_completed_at == "2099-01-15T01:30:00Z"
    assert completed.next_due_at is None
    assert service.list() == ()
    assert service.get(completed.routine_id).status == "COMPLETED"

    with pytest.raises(RoutineConflictError, match="cannot be scheduler-linked"):
        service.link_scheduler(completed.routine_id, "cron-one-off")


def test_recurring_completion_records_occurrence_and_remains_active(service) -> None:
    pending = service.create(
        "Synthetic filter check",
        "RECURRING",
        "0 8 * * 1",
        "Asia/Jakarta",
    )
    service.link_scheduler(pending.routine_id, "cron-recurring")

    completed_occurrence = service.complete(pending.routine_id)

    assert completed_occurrence.status == "ACTIVE"
    assert completed_occurrence.last_completed_at == "2099-01-15T01:30:00Z"
    assert completed_occurrence.next_due_at == "2099-01-19T08:00:00+07:00"
    assert service.list() == (completed_occurrence,)


def test_pending_and_active_routines_can_be_cancelled_authoritatively(service) -> None:
    pending = service.create(
        "Synthetic pending", "RECURRING", "0 9 * * *", "Asia/Jakarta"
    )
    active = service.create(
        "Synthetic active", "RECURRING", "0 10 * * *", "Asia/Jakarta"
    )
    service.link_scheduler(active.routine_id, "cron-active")

    cancelled_pending = service.cancel(pending.routine_id)
    cancelled_active = service.cancel(active.routine_id)

    assert cancelled_pending.status == "CANCELLED"
    assert cancelled_pending.scheduler_job_id is None
    assert cancelled_active.status == "CANCELLED"
    assert cancelled_active.scheduler_job_id == "cron-active"
    assert service.list() == ()
    assert service.cancel(active.routine_id) == cancelled_active


def test_list_orders_by_derived_next_due_and_excludes_terminal_state(service) -> None:
    later = service.create(
        "Synthetic later", "RECURRING", "0 10 20 * *", "Asia/Jakarta"
    )
    earlier = service.create(
        "Synthetic earlier",
        "ONE_OFF",
        "2099-01-15T18:00:00+07:00",
        "Asia/Jakarta",
    )
    cancelled = service.create(
        "Synthetic cancelled", "RECURRING", "0 7 * * *", "Asia/Jakarta"
    )
    service.link_scheduler(later.routine_id, "cron-later")
    service.link_scheduler(earlier.routine_id, "cron-earlier")
    service.cancel(cancelled.routine_id)

    assert [routine.title for routine in service.list()] == [
        "Synthetic earlier",
        "Synthetic later",
    ]
    assert {routine.status for routine in service.list(include_inactive=True)} == {
        "ACTIVE",
        "CANCELLED",
    }


def test_routine_history_cannot_be_hard_deleted(service, database) -> None:
    routine = service.create(
        "Synthetic immutable history", "RECURRING", "0 9 * * *", "Asia/Jakarta"
    )

    with database.connect() as connection:
        with pytest.raises(sqlite3.IntegrityError, match="cannot be deleted"):
            connection.execute("DELETE FROM household_routines WHERE id = ?", (routine.routine_id,))
