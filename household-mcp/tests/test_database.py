from __future__ import annotations

import os
import sqlite3
from uuid import uuid4

import pytest

from faria_household_mcp.allocation import (
    AllocationConflictError,
    InvalidAllocationStateError,
    MonthlyAllocationService,
)
from faria_household_mcp.database import HouseholdDatabase, default_database_path


@pytest.fixture
def database(tmp_path) -> HouseholdDatabase:
    return HouseholdDatabase(tmp_path / "nested" / "faria.db")


@pytest.fixture
def service(database) -> MonthlyAllocationService:
    return MonthlyAllocationService(database)


def test_new_database_initializes_once_and_enables_foreign_keys(database) -> None:
    database.initialize()
    database.initialize()

    with database.connect() as connection:
        migration_count = connection.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0]
        foreign_keys = connection.execute("PRAGMA foreign_keys").fetchone()[0]

    assert migration_count == 1
    assert foreign_keys == 1
    assert database.path.exists()
    assert database.path.parent.exists()
    assert os.stat(database.path).st_mode & 0o777 == 0o600


def test_database_path_defaults_outside_repository_and_supports_override(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("FARIA_DB_PATH", raising=False)
    assert default_database_path().as_posix().endswith("/.faria/data/faria.db")

    override = tmp_path / "custom.db"
    monkeypatch.setenv("FARIA_DB_PATH", str(override))
    assert default_database_path() == override


def test_get_separates_non_authoritative_draft_from_confirmed_state(service) -> None:
    draft = service.save_draft("2099-01", 1_000_000, [])

    state = service.get("2099-01")

    assert state.draft == draft
    assert state.confirmed is None


def test_confirmation_is_atomic_authoritative_and_idempotent(service) -> None:
    draft = service.save_draft(
        "2099-01",
        1_000_000,
        [{"category": "savings", "label": "Test Goal", "amount_idr": 400_000}],
    )

    confirmed = service.confirm(draft.allocation_id, confirmation_reference="synthetic-test")
    repeated = service.confirm(draft.allocation_id, confirmation_reference="ignored-retry")

    assert confirmed.status == "CONFIRMED"
    assert confirmed.authoritative is True
    assert confirmed.confirmed_at is not None
    assert confirmed.confirmation_reference == "synthetic-test"
    assert repeated == confirmed
    assert repeated.items == draft.items


def test_conflicting_confirmation_fails_without_mutating_second_draft(service) -> None:
    first = service.save_draft("2099-01", 1_000_000, [])
    service.confirm(first.allocation_id)
    second = service.save_draft(
        "2099-01",
        2_000_000,
        [{"category": "buffer", "amount_idr": 100_000}],
    )

    with pytest.raises(AllocationConflictError, match="already has a confirmed allocation"):
        service.confirm(second.allocation_id)

    state = service.get("2099-01")
    assert state.confirmed is not None
    assert state.confirmed.allocation_id == first.allocation_id
    assert state.draft is not None
    assert state.draft.allocation_id == second.allocation_id
    assert state.draft.status == "DRAFT"


def test_database_constraint_enforces_one_confirmed_allocation_per_period(database) -> None:
    database.initialize()
    now = "2099-01-01T00:00:00Z"
    with database.connect() as connection:
        connection.execute("BEGIN IMMEDIATE")
        confirmed_id = str(uuid4())
        draft_id = str(uuid4())
        connection.execute(
            """
            INSERT INTO monthly_allocations (
                id, period, income_idr, status, created_at, updated_at, confirmed_at
            ) VALUES (?, '2099-01', 1000000, 'CONFIRMED', ?, ?, ?)
            """,
            (confirmed_id, now, now, now),
        )
        connection.execute(
            """
            INSERT INTO monthly_allocations (
                id, period, income_idr, status, created_at, updated_at, confirmed_at
            ) VALUES (?, '2099-01', 1000000, 'DRAFT', ?, ?, NULL)
            """,
            (draft_id, now, now),
        )
        connection.commit()
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "UPDATE monthly_allocations SET status = 'CONFIRMED', confirmed_at = ? WHERE id = ?",
                (now, draft_id),
            )


def test_draft_can_be_discarded_but_confirmed_allocation_cannot(service) -> None:
    draft = service.save_draft("2099-01", 1_000_000, [])
    discarded = service.discard_draft(draft.allocation_id)

    assert discarded.status == "DISCARDED"
    assert discarded.authoritative is False

    next_draft = service.save_draft("2099-02", 1_000_000, [])
    confirmed = service.confirm(next_draft.allocation_id)
    with pytest.raises(InvalidAllocationStateError, match="cannot be discarded"):
        service.discard_draft(confirmed.allocation_id)
