from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict

from faria_household_mcp.allocation import validate_period
from faria_household_mcp.database import utc_now

if TYPE_CHECKING:
    from faria_household_mcp.database import HouseholdDatabase


GivingType = Literal["zakat_penghasilan", "sedekah"]


class GivingError(Exception):
    """Base error for expected giving-domain failures."""


class GivingValidationError(GivingError):
    """Raised when caller input violates the giving contract."""


class GivingConflictError(GivingError):
    """Raised when a request conflicts with immutable giving history."""


class GivingRecordView(BaseModel):
    model_config = ConfigDict(frozen=True)

    giving_record_id: str
    type: GivingType
    amount_idr: int
    period: str
    recorded_at: str
    monthly_allocation_reference: str | None
    note: str | None


def _giving_type(value: object) -> GivingType:
    if type(value) is not str or value not in {"zakat_penghasilan", "sedekah"}:
        raise GivingValidationError("type must be zakat_penghasilan or sedekah")
    return value  # type: ignore[return-value]


def _positive_integer(value: object) -> int:
    if type(value) is not int or value <= 0:
        raise GivingValidationError("amount_idr must be a positive integer")
    return value


def _valid_period(value: object) -> str:
    try:
        return validate_period(value)
    except Exception as error:
        raise GivingValidationError("period must use YYYY-MM with a valid month") from error


def _optional_text(value: object, field: str) -> str | None:
    if value is None:
        return None
    if type(value) is not str or not value.strip():
        raise GivingValidationError(f"{field} must be a non-blank string")
    return value.strip()


def _optional_uuid(value: object) -> str | None:
    if value is None:
        return None
    if type(value) is not str:
        raise GivingValidationError("monthly_allocation_reference must be a UUID string")
    try:
        parsed = UUID(value)
    except ValueError as error:
        raise GivingValidationError("monthly_allocation_reference must be a UUID string") from error
    if str(parsed) != value:
        raise GivingValidationError(
            "monthly_allocation_reference must be a canonical UUID string"
        )
    return value


class GivingService:
    def __init__(self, database: HouseholdDatabase) -> None:
        self._database = database

    def list_records(
        self,
        period: object = None,
        type: object = None,
    ) -> tuple[GivingRecordView, ...]:
        valid_period = None if period is None else _valid_period(period)
        valid_type = None if type is None else _giving_type(type)
        self._database.initialize()
        clauses: list[str] = []
        parameters: list[object] = []
        if valid_period is not None:
            clauses.append("period = ?")
            parameters.append(valid_period)
        if valid_type is not None:
            clauses.append("type = ?")
            parameters.append(valid_type)
        query = "SELECT * FROM giving_records"
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY rowid"
        with self._database.connect() as connection:
            rows = connection.execute(query, tuple(parameters)).fetchall()
        return tuple(self._from_row(row) for row in rows)

    def record(
        self,
        type: object,
        amount_idr: object,
        period: object,
        monthly_allocation_reference: object = None,
        note: object = None,
    ) -> GivingRecordView:
        valid_type = _giving_type(type)
        valid_amount = _positive_integer(amount_idr)
        valid_period = _valid_period(period)
        valid_reference = _optional_uuid(monthly_allocation_reference)
        valid_note = _optional_text(note, "note")
        self._database.initialize()

        with self._database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                if valid_reference is not None:
                    allocation = connection.execute(
                        "SELECT period, status FROM monthly_allocations WHERE id = ?",
                        (valid_reference,),
                    ).fetchone()
                    if allocation is None or allocation["status"] != "CONFIRMED":
                        raise GivingValidationError(
                            "monthly_allocation_reference must identify a confirmed allocation"
                        )
                    if allocation["period"] != valid_period:
                        raise GivingValidationError(
                            "monthly_allocation_reference period must match giving period"
                        )
                    existing = connection.execute(
                        """
                        SELECT * FROM giving_records
                        WHERE period = ? AND type = ? AND monthly_allocation_reference = ?
                        """,
                        (valid_period, valid_type, valid_reference),
                    ).fetchone()
                    if existing is not None:
                        if existing["amount_idr"] != valid_amount:
                            raise GivingConflictError(
                                "linked giving record already exists with a different amount"
                            )
                        connection.commit()
                        return self._from_row(existing)

                record_id = str(uuid4())
                connection.execute(
                    """
                    INSERT INTO giving_records (
                        id, type, amount_idr, period, recorded_at,
                        monthly_allocation_reference, note
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record_id,
                        valid_type,
                        valid_amount,
                        valid_period,
                        utc_now(),
                        valid_reference,
                        valid_note,
                    ),
                )
                connection.commit()
            except Exception:
                connection.rollback()
                raise

            row = connection.execute(
                "SELECT * FROM giving_records WHERE id = ?", (record_id,)
            ).fetchone()
            assert row is not None
            return self._from_row(row)

    @staticmethod
    def _from_row(row: sqlite3.Row) -> GivingRecordView:
        return GivingRecordView(
            giving_record_id=row["id"],
            type=row["type"],
            amount_idr=row["amount_idr"],
            period=row["period"],
            recorded_at=row["recorded_at"],
            monthly_allocation_reference=row["monthly_allocation_reference"],
            note=row["note"],
        )
