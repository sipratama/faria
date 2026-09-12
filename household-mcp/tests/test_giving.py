from __future__ import annotations

import sqlite3

import pytest

from faria_household_mcp.allocation import MonthlyAllocationService
from faria_household_mcp.database import HouseholdDatabase
from faria_household_mcp.giving import (
    GivingConflictError,
    GivingService,
    GivingValidationError,
)


@pytest.fixture
def database(tmp_path) -> HouseholdDatabase:
    return HouseholdDatabase(tmp_path / "faria.db")


@pytest.fixture
def service(database) -> GivingService:
    return GivingService(database)


def test_record_and_filter_zakat_and_sedekah(service) -> None:
    zakat = service.record("zakat_penghasilan", 250_000, "2099-01", note="Synthetic zakat")
    sedekah = service.record("sedekah", 100_000, "2099-01")
    service.record("sedekah", 50_000, "2099-02")

    assert zakat.type == "zakat_penghasilan"
    assert sedekah.type == "sedekah"
    assert service.list_records(period="2099-01") == (zakat, sedekah)
    assert service.list_records(type="zakat_penghasilan") == (zakat,)


@pytest.mark.parametrize("giving_type", ["zakat", "charity", "", None, 1])
def test_invalid_giving_type_is_rejected(service, giving_type) -> None:
    with pytest.raises(GivingValidationError, match="type"):
        service.record(giving_type, 100_000, "2099-01")


@pytest.mark.parametrize("amount", [0, -1, True, 1.5, "1000", None])
def test_giving_amount_must_be_positive_integer(service, amount) -> None:
    with pytest.raises(GivingValidationError, match="amount_idr"):
        service.record("sedekah", amount, "2099-01")


@pytest.mark.parametrize("period", ["2099-1", "2099-00", "2099-13", "not-a-period", 209901])
def test_giving_period_must_be_valid(service, period) -> None:
    with pytest.raises(GivingValidationError, match="period"):
        service.record("sedekah", 100_000, period)


def test_retry_for_same_allocation_fulfillment_is_idempotent(database, service) -> None:
    allocation_service = MonthlyAllocationService(database)
    draft = allocation_service.save_draft(
        "2099-01",
        1_000_000,
        [{"category": "zakat", "amount_idr": 25_000}],
    )
    allocation = allocation_service.confirm(draft.allocation_id)

    first = service.record(
        "zakat_penghasilan",
        25_000,
        "2099-01",
        monthly_allocation_reference=allocation.allocation_id,
    )
    repeated = service.record(
        "zakat_penghasilan",
        25_000,
        "2099-01",
        monthly_allocation_reference=allocation.allocation_id,
    )

    assert repeated == first
    assert service.list_records() == (first,)


def test_retry_with_different_amount_conflicts(database, service) -> None:
    allocation_service = MonthlyAllocationService(database)
    draft = allocation_service.save_draft("2099-01", 1_000_000, [])
    allocation = allocation_service.confirm(draft.allocation_id)
    service.record(
        "zakat_penghasilan",
        25_000,
        "2099-01",
        monthly_allocation_reference=allocation.allocation_id,
    )

    with pytest.raises(GivingConflictError, match="different amount"):
        service.record(
            "zakat_penghasilan",
            30_000,
            "2099-01",
            monthly_allocation_reference=allocation.allocation_id,
        )


def test_multiple_unreferenced_sedekah_records_in_one_month_are_allowed(service) -> None:
    first = service.record("sedekah", 100_000, "2099-01")
    second = service.record("sedekah", 50_000, "2099-01")

    assert first.giving_record_id != second.giving_record_id
    assert service.list_records(period="2099-01", type="sedekah") == (first, second)


def test_giving_reference_must_match_a_confirmed_allocation_period(database, service) -> None:
    allocation_service = MonthlyAllocationService(database)
    draft = allocation_service.save_draft("2099-01", 1_000_000, [])

    with pytest.raises(GivingValidationError, match="confirmed allocation"):
        service.record(
            "sedekah",
            10_000,
            "2099-01",
            monthly_allocation_reference=draft.allocation_id,
        )

    allocation_service.confirm(draft.allocation_id)
    with pytest.raises(GivingValidationError, match="period"):
        service.record(
            "sedekah",
            10_000,
            "2099-02",
            monthly_allocation_reference=draft.allocation_id,
        )


def test_giving_history_is_immutable_at_database_boundary(database, service) -> None:
    record = service.record("sedekah", 100_000, "2099-01")

    with database.connect() as connection:
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            connection.execute(
                "UPDATE giving_records SET amount_idr = 200000 WHERE id = ?",
                (record.giving_record_id,),
            )
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            connection.execute(
                "DELETE FROM giving_records WHERE id = ?",
                (record.giving_record_id,),
            )
