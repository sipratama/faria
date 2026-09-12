from __future__ import annotations

import pytest

from faria_household_mcp.allocation import (
    AllocationValidationError,
    MonthlyAllocationService,
)
from faria_household_mcp.database import HouseholdDatabase


@pytest.fixture
def service(tmp_path) -> MonthlyAllocationService:
    return MonthlyAllocationService(HouseholdDatabase(tmp_path / "faria.db"))


def test_valid_draft_is_non_authoritative_and_calculates_remainder(service) -> None:
    draft = service.save_draft(
        period="2099-01",
        income_idr=10_000_000,
        items=[
            {"category": "zakat", "amount_idr": 250_000},
            {"category": "sedekah", "amount_idr": 150_000},
            {"category": "savings", "label": "Test Goal", "amount_idr": 2_000_000},
            {"category": "household_budget", "amount_idr": 4_000_000},
            {"category": "personal_allowance", "label": "Person A", "amount_idr": 1_000_000},
            {"category": "buffer", "amount_idr": 500_000},
        ],
    )

    assert draft.status == "DRAFT"
    assert draft.authoritative is False
    assert draft.allocated_total_idr == 7_900_000
    assert draft.remainder_idr == 2_100_000


@pytest.mark.parametrize("income_idr", [0, -1, True, 1.5, "1000000", None])
def test_income_must_be_a_positive_integer(service, income_idr) -> None:
    with pytest.raises(AllocationValidationError, match="income_idr"):
        service.save_draft("2099-01", income_idr, [])


@pytest.mark.parametrize("amount_idr", [-1, True, 1.5, "1000", None])
def test_item_amount_must_be_a_non_negative_integer(service, amount_idr) -> None:
    with pytest.raises(AllocationValidationError, match="amount_idr"):
        service.save_draft(
            "2099-01",
            1_000_000,
            [{"category": "savings", "amount_idr": amount_idr}],
        )


@pytest.mark.parametrize("period", ["2099-1", "99-01", "2099-00", "2099-13", "2099/01", 209901])
def test_period_must_use_valid_yyyy_mm(service, period) -> None:
    with pytest.raises(AllocationValidationError, match="period"):
        service.save_draft(period, 1_000_000, [])


def test_category_must_be_supported(service) -> None:
    with pytest.raises(AllocationValidationError, match="category"):
        service.save_draft(
            "2099-01",
            1_000_000,
            [{"category": "investment", "amount_idr": 100_000}],
        )


def test_total_allocated_cannot_exceed_income(service) -> None:
    with pytest.raises(AllocationValidationError, match="exceeds income_idr"):
        service.save_draft(
            "2099-01",
            1_000_000,
            [
                {"category": "household_budget", "amount_idr": 900_000},
                {"category": "buffer", "amount_idr": 100_001},
            ],
        )


def test_saving_again_updates_the_current_draft(service) -> None:
    original = service.save_draft(
        "2099-01",
        1_000_000,
        [{"category": "buffer", "amount_idr": 100_000}],
    )
    updated = service.save_draft(
        "2099-01",
        2_000_000,
        [{"category": "buffer", "amount_idr": 250_000}],
    )

    assert updated.allocation_id == original.allocation_id
    assert updated.income_idr == 2_000_000
    assert updated.items[0].amount_idr == 250_000
    assert updated.remainder_idr == 1_750_000


def test_multiple_savings_items_can_represent_separate_goal_allocations(service) -> None:
    draft = service.save_draft(
        "2099-01",
        2_000_000,
        [
            {"category": "savings", "label": "Synthetic Goal A", "amount_idr": 400_000},
            {"category": "savings", "label": "Synthetic Goal B", "amount_idr": 600_000},
        ],
    )

    assert [(item.category, item.label) for item in draft.items] == [
        ("savings", "Synthetic Goal A"),
        ("savings", "Synthetic Goal B"),
    ]


def test_positive_remainder_can_be_confirmed_without_a_buffer_item(service) -> None:
    draft = service.save_draft(
        "2099-01",
        1_000_000,
        [{"category": "household_budget", "amount_idr": 600_000}],
    )

    confirmed = service.confirm(draft.allocation_id, "explicit-unallocated-remainder")

    assert confirmed.status == "CONFIRMED"
    assert confirmed.remainder_idr == 400_000
    assert all(item.category != "buffer" for item in confirmed.items)
