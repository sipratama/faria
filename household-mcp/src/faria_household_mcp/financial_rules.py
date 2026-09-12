from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from faria_household_mcp.database import HouseholdDatabase


class FinancialRulesError(Exception):
    """Base error for expected household financial-rule failures."""


class FinancialRulesValidationError(FinancialRulesError):
    """Raised when input violates the financial-rule calculation contract."""


class FinancialRulesView(BaseModel):
    """The authoritative singleton household financial rules."""

    model_config = ConfigDict(frozen=True)

    zakat_basis: Literal["THP"]
    zakat_rate_basis_points: int
    sedekah_mode: Literal["MANUAL"]
    savings_mode: Literal["GOAL_BASED"]
    remainder_policy: Literal["ASK_ALLOW_UNALLOCATED"]
    created_at: str
    updated_at: str


class ZakatCalculationView(BaseModel):
    """Deterministic result calculated from the authoritative household rule."""

    model_config = ConfigDict(frozen=True)

    thp_idr: int
    basis: Literal["THP"]
    rate_basis_points: int
    amount_idr: int


class FinancialRulesService:
    def __init__(self, database: HouseholdDatabase) -> None:
        self._database = database

    def get(self) -> FinancialRulesView:
        self._database.initialize()
        with self._database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM household_financial_rules WHERE id = 1"
            ).fetchone()
        if row is None:
            raise FinancialRulesError("authoritative household financial rules are unavailable")
        return FinancialRulesView(
            zakat_basis=row["zakat_basis"],
            zakat_rate_basis_points=row["zakat_rate_basis_points"],
            sedekah_mode=row["sedekah_mode"],
            savings_mode=row["savings_mode"],
            remainder_policy=row["remainder_policy"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def calculate_zakat(self, thp_idr: object) -> ZakatCalculationView:
        if type(thp_idr) is not int or thp_idr <= 0:
            raise FinancialRulesValidationError("thp_idr must be a positive integer")

        rules = self.get()
        amount_idr = (thp_idr * rules.zakat_rate_basis_points + 5_000) // 10_000
        return ZakatCalculationView(
            thp_idr=thp_idr,
            basis=rules.zakat_basis,
            rate_basis_points=rules.zakat_rate_basis_points,
            amount_idr=amount_idr,
        )
