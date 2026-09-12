from __future__ import annotations

import sqlite3

import pytest

from faria_household_mcp.allocation import MonthlyAllocationService
from faria_household_mcp.database import HouseholdDatabase
from faria_household_mcp.savings import (
    SavingsConflictError,
    SavingsNotFoundError,
    SavingsService,
    SavingsValidationError,
)


@pytest.fixture
def database(tmp_path) -> HouseholdDatabase:
    return HouseholdDatabase(tmp_path / "faria.db")


@pytest.fixture
def service(database) -> SavingsService:
    return SavingsService(database)


def test_create_goal_persists_description_optional_date_and_zero_progress(service) -> None:
    goal = service.create_goal(
        name="Synthetic Camera Fund",
        description="Synthetic test goal",
        target_amount_idr=12_000_000,
        target_date="2099-12-31",
    )

    assert goal.name == "Synthetic Camera Fund"
    assert goal.description == "Synthetic test goal"
    assert goal.target_amount_idr == 12_000_000
    assert goal.current_amount_idr == 0
    assert goal.target_date == "2099-12-31"
    assert goal.status == "ACTIVE"


@pytest.mark.parametrize("name", ["", "   ", None, 123])
def test_goal_name_is_required(service, name) -> None:
    with pytest.raises(SavingsValidationError, match="name"):
        service.create_goal(name, 1_000_000)


@pytest.mark.parametrize("amount", [0, -1, True, 1.5, "1000", None])
def test_goal_target_must_be_a_positive_integer(service, amount) -> None:
    with pytest.raises(SavingsValidationError, match="target_amount_idr"):
        service.create_goal("Synthetic Goal", amount)


@pytest.mark.parametrize("target_date", ["2099-02-30", "2099-2-01", "not-a-date", 20990101])
def test_goal_target_date_must_be_a_valid_iso_date(service, target_date) -> None:
    with pytest.raises(SavingsValidationError, match="target_date"):
        service.create_goal("Synthetic Goal", 1_000_000, target_date=target_date)


def test_list_and_get_return_authoritative_goal_progress(service) -> None:
    first = service.create_goal("Synthetic Goal A", 1_000_000)
    service.create_goal("Synthetic Goal B", 2_000_000)

    listed = service.list_goals()
    fetched = service.get_goal(first.goal_id)

    assert [goal.name for goal in listed] == ["Synthetic Goal A", "Synthetic Goal B"]
    assert fetched == first


def test_goal_get_rejects_unknown_id(service) -> None:
    with pytest.raises(SavingsNotFoundError, match="was not found"):
        service.get_goal("00000000-0000-4000-8000-000000000000")


def test_multiple_contributions_accumulate_and_complete_goal(service) -> None:
    goal = service.create_goal("Synthetic Appliance Fund", 1_000_000)

    first = service.record_contribution(goal.goal_id, 400_000, note="Synthetic first contribution")
    second = service.record_contribution(goal.goal_id, 700_000)

    assert first.goal.current_amount_idr == 400_000
    assert first.goal.status == "ACTIVE"
    assert second.goal.current_amount_idr == 1_100_000
    assert second.goal.status == "COMPLETED"
    assert service.get_goal(goal.goal_id) == second.goal
    assert first.contribution.contribution_id != second.contribution.contribution_id


@pytest.mark.parametrize("amount", [0, -1, True, 1.5, "1000", None])
def test_contribution_amount_must_be_a_positive_integer(service, amount) -> None:
    goal = service.create_goal("Synthetic Goal", 1_000_000)
    with pytest.raises(SavingsValidationError, match="amount_idr"):
        service.record_contribution(goal.goal_id, amount)


def test_linked_contribution_retry_is_idempotent(database, service) -> None:
    allocation_service = MonthlyAllocationService(database)
    draft = allocation_service.save_draft(
        "2099-01",
        2_000_000,
        [{"category": "savings", "label": "Synthetic Goal", "amount_idr": 500_000}],
    )
    allocation = allocation_service.confirm(draft.allocation_id)
    goal = service.create_goal("Synthetic Goal", 1_000_000)

    first = service.record_contribution(
        goal.goal_id,
        500_000,
        source_allocation_reference=allocation.allocation_id,
    )
    repeated = service.record_contribution(
        goal.goal_id,
        500_000,
        source_allocation_reference=allocation.allocation_id,
    )

    assert repeated == first
    assert service.get_goal(goal.goal_id).current_amount_idr == 500_000


def test_linked_contribution_retry_with_different_amount_conflicts(database, service) -> None:
    allocation_service = MonthlyAllocationService(database)
    draft = allocation_service.save_draft("2099-01", 2_000_000, [])
    allocation = allocation_service.confirm(draft.allocation_id)
    goal = service.create_goal("Synthetic Goal", 1_000_000)
    service.record_contribution(
        goal.goal_id,
        400_000,
        source_allocation_reference=allocation.allocation_id,
    )

    with pytest.raises(SavingsConflictError, match="different amount"):
        service.record_contribution(
            goal.goal_id,
            500_000,
            source_allocation_reference=allocation.allocation_id,
        )


def test_contribution_reference_must_identify_a_confirmed_allocation(database, service) -> None:
    allocation_service = MonthlyAllocationService(database)
    draft = allocation_service.save_draft("2099-01", 2_000_000, [])
    goal = service.create_goal("Synthetic Referenced Goal", 1_000_000)

    with pytest.raises(SavingsValidationError, match="confirmed allocation"):
        service.record_contribution(
            goal.goal_id,
            500_000,
            source_allocation_reference=draft.allocation_id,
        )


def test_contribution_history_is_immutable_at_database_boundary(database, service) -> None:
    goal = service.create_goal("Synthetic Immutable Goal", 1_000_000)
    result = service.record_contribution(goal.goal_id, 100_000)

    with database.connect() as connection:
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            connection.execute(
                "UPDATE savings_contributions SET amount_idr = 200000 WHERE id = ?",
                (result.contribution.contribution_id,),
            )
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            connection.execute(
                "DELETE FROM savings_contributions WHERE id = ?",
                (result.contribution.contribution_id,),
            )
