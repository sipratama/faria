from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StrictInt, ValidationError, field_validator

if TYPE_CHECKING:
    from faria_household_mcp.database import HouseholdDatabase


AllocationCategory = Literal[
    "zakat",
    "sedekah",
    "savings",
    "household_budget",
    "personal_allowance",
    "buffer",
]
AllocationStatus = Literal["DRAFT", "CONFIRMED", "DISCARDED"]

_PERIOD_PATTERN = re.compile(r"^[0-9]{4}-(0[1-9]|1[0-2])$")


class AllocationError(Exception):
    """Base error for expected monthly-allocation failures."""


class AllocationValidationError(AllocationError):
    """Raised when caller input violates the allocation contract."""


class AllocationNotFoundError(AllocationError):
    """Raised when an allocation ID does not exist."""


class AllocationConflictError(AllocationError):
    """Raised when a period already has an authoritative allocation."""


class InvalidAllocationStateError(AllocationError):
    """Raised when a requested state transition is not allowed."""


class AllocationItemInput(BaseModel):
    """Strict caller-supplied allocation item."""

    model_config = ConfigDict(extra="forbid", strict=True)

    category: AllocationCategory
    label: str | None = None
    amount_idr: StrictInt

    @field_validator("label")
    @classmethod
    def validate_label(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("label must not be blank")
        return normalized


class AllocationItemView(BaseModel):
    """Allocation item returned through the MCP boundary."""

    model_config = ConfigDict(frozen=True)

    category: AllocationCategory
    label: str | None
    amount_idr: int


class AllocationView(BaseModel):
    """Complete persisted allocation state with deterministic totals."""

    model_config = ConfigDict(frozen=True)

    allocation_id: str
    period: str
    income_idr: int
    status: AllocationStatus
    items: tuple[AllocationItemView, ...]
    allocated_total_idr: int
    remainder_idr: int
    authoritative: bool
    created_at: str
    updated_at: str
    confirmed_at: str | None
    confirmation_reference: str | None


class PeriodAllocationView(BaseModel):
    """Current authoritative and draft state for one period."""

    model_config = ConfigDict(frozen=True)

    period: str
    confirmed: AllocationView | None
    draft: AllocationView | None


def validate_period(period: object) -> str:
    if type(period) is not str or not _PERIOD_PATTERN.fullmatch(period):
        raise AllocationValidationError("period must use YYYY-MM with a valid month")
    return period


def validate_income(income_idr: object) -> int:
    if type(income_idr) is not int or income_idr <= 0:
        raise AllocationValidationError("income_idr must be a positive integer")
    return income_idr


def validate_allocation_id(allocation_id: object) -> str:
    if type(allocation_id) is not str:
        raise AllocationValidationError("allocation_id must be a UUID string")
    try:
        parsed = UUID(allocation_id)
    except ValueError as error:
        raise AllocationValidationError("allocation_id must be a UUID string") from error
    if str(parsed) != allocation_id:
        raise AllocationValidationError("allocation_id must be a canonical UUID string")
    return allocation_id


def validate_confirmation_reference(reference: object) -> str | None:
    if reference is None:
        return None
    if type(reference) is not str or not reference.strip():
        raise AllocationValidationError("confirmation_reference must be a non-blank string")
    return reference.strip()


def normalize_items(items: object) -> tuple[AllocationItemInput, ...]:
    if isinstance(items, (str, bytes)) or not isinstance(items, Sequence):
        raise AllocationValidationError("items must be a list of allocation items")

    normalized: list[AllocationItemInput] = []
    for index, item in enumerate(items):
        try:
            if isinstance(item, AllocationItemInput):
                parsed = item
            elif isinstance(item, Mapping):
                parsed = AllocationItemInput.model_validate(item, strict=True)
            else:
                raise AllocationValidationError(f"items[{index}] must be an object")
        except ValidationError as error:
            detail = error.errors()[0]
            field = ".".join(str(part) for part in detail["loc"])
            raise AllocationValidationError(
                f"items[{index}].{field} is invalid: {detail['msg']}"
            ) from error

        if type(parsed.amount_idr) is not int or parsed.amount_idr < 0:
            raise AllocationValidationError(f"items[{index}].amount_idr must be a non-negative integer")
        normalized.append(parsed)

    return tuple(normalized)


class MonthlyAllocationService:
    """Applies allocation validation and delegates atomic persistence."""

    def __init__(self, database: HouseholdDatabase) -> None:
        self._database = database

    def get(self, period: object) -> PeriodAllocationView:
        return self._database.get_period_state(validate_period(period))

    def save_draft(
        self,
        period: object,
        income_idr: object,
        items: object,
    ) -> AllocationView:
        valid_period = validate_period(period)
        valid_income = validate_income(income_idr)
        valid_items = normalize_items(items)
        allocated_total = sum(item.amount_idr for item in valid_items)
        if allocated_total > valid_income:
            raise AllocationValidationError("allocated_total_idr exceeds income_idr")
        return self._database.save_draft(valid_period, valid_income, valid_items)

    def confirm(
        self,
        allocation_id: object,
        confirmation_reference: object = None,
    ) -> AllocationView:
        return self._database.confirm(
            validate_allocation_id(allocation_id),
            validate_confirmation_reference(confirmation_reference),
        )

    def discard_draft(self, allocation_id: object) -> AllocationView:
        return self._database.discard_draft(validate_allocation_id(allocation_id))
