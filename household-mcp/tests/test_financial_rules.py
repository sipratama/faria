from __future__ import annotations

import pytest

from faria_household_mcp.database import HouseholdDatabase
from faria_household_mcp.financial_rules import (
    FinancialRulesService,
    FinancialRulesValidationError,
)


@pytest.fixture
def database(tmp_path) -> HouseholdDatabase:
    return HouseholdDatabase(tmp_path / "faria.db")


@pytest.fixture
def service(database) -> FinancialRulesService:
    return FinancialRulesService(database)


def test_default_rules_are_initialized_once_with_household_decisions(database, service) -> None:
    database.initialize()
    database.initialize()

    rules = service.get()
    with database.connect() as connection:
        count = connection.execute("SELECT COUNT(*) FROM household_financial_rules").fetchone()[0]

    assert count == 1
    assert rules.zakat_basis == "THP"
    assert rules.zakat_rate_basis_points == 250
    assert rules.sedekah_mode == "MANUAL"
    assert rules.savings_mode == "GOAL_BASED"
    assert rules.remainder_policy == "ASK_ALLOW_UNALLOCATED"


def test_reinitialization_does_not_overwrite_an_existing_rule_set(database, service) -> None:
    database.initialize()
    with database.connect() as connection:
        connection.execute(
            "UPDATE household_financial_rules SET zakat_rate_basis_points = 300 WHERE id = 1"
        )

    database.initialize()

    assert service.get().zakat_rate_basis_points == 300


@pytest.mark.parametrize(
    ("thp_idr", "expected_amount_idr"),
    [
        (25_000_000, 625_000),
        (20, 1),
        (60, 2),
        (101, 3),
        (9_007_199_254_740_993, 225_179_981_368_525),
    ],
)
def test_zakat_uses_exact_250_basis_point_round_half_up_calculation(
    service, thp_idr, expected_amount_idr
) -> None:
    result = service.calculate_zakat(thp_idr)

    assert result.thp_idr == thp_idr
    assert result.basis == "THP"
    assert result.rate_basis_points == 250
    assert result.amount_idr == expected_amount_idr


def test_zakat_calculation_reads_the_authoritative_rule(database, service) -> None:
    database.initialize()
    with database.connect() as connection:
        connection.execute(
            "UPDATE household_financial_rules SET zakat_rate_basis_points = 300 WHERE id = 1"
        )

    assert service.calculate_zakat(1_000).amount_idr == 30


@pytest.mark.parametrize("thp_idr", [0, -1, True, 1.5, "1000", None])
def test_zakat_thp_must_be_a_positive_strict_integer(service, thp_idr) -> None:
    with pytest.raises(FinancialRulesValidationError, match="thp_idr"):
        service.calculate_zakat(thp_idr)
