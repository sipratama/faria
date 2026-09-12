from __future__ import annotations

import sqlite3
from datetime import date
from typing import TYPE_CHECKING, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict

from faria_household_mcp.database import utc_now

if TYPE_CHECKING:
    from faria_household_mcp.database import HouseholdDatabase


SavingsGoalStatus = Literal["ACTIVE", "COMPLETED", "ARCHIVED"]


class SavingsError(Exception):
    """Base error for expected savings-domain failures."""


class SavingsValidationError(SavingsError):
    """Raised when caller input violates the savings contract."""


class SavingsNotFoundError(SavingsError):
    """Raised when a requested savings goal does not exist."""


class SavingsConflictError(SavingsError):
    """Raised when an operation conflicts with existing savings history."""


class SavingsGoalView(BaseModel):
    model_config = ConfigDict(frozen=True)

    goal_id: str
    name: str
    description: str | None
    target_amount_idr: int
    current_amount_idr: int
    target_date: str | None
    status: SavingsGoalStatus
    created_at: str
    updated_at: str


class SavingsContributionView(BaseModel):
    model_config = ConfigDict(frozen=True)

    contribution_id: str
    goal_id: str
    amount_idr: int
    recorded_at: str
    source_allocation_reference: str | None
    note: str | None


class SavingsContributionResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    contribution: SavingsContributionView
    goal: SavingsGoalView


def _required_text(value: object, field: str) -> str:
    if type(value) is not str or not value.strip():
        raise SavingsValidationError(f"{field} must be a non-blank string")
    return value.strip()


def _optional_text(value: object, field: str) -> str | None:
    if value is None:
        return None
    return _required_text(value, field)


def _positive_integer(value: object, field: str) -> int:
    if type(value) is not int or value <= 0:
        raise SavingsValidationError(f"{field} must be a positive integer")
    return value


def _canonical_uuid(value: object, field: str) -> str:
    if type(value) is not str:
        raise SavingsValidationError(f"{field} must be a UUID string")
    try:
        parsed = UUID(value)
    except ValueError as error:
        raise SavingsValidationError(f"{field} must be a UUID string") from error
    if str(parsed) != value:
        raise SavingsValidationError(f"{field} must be a canonical UUID string")
    return value


def _optional_date(value: object) -> str | None:
    if value is None:
        return None
    if type(value) is not str:
        raise SavingsValidationError("target_date must be a valid ISO date")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise SavingsValidationError("target_date must be a valid ISO date") from error
    if parsed.isoformat() != value:
        raise SavingsValidationError("target_date must be a valid ISO date")
    return value


def _status(value: object | None) -> SavingsGoalStatus | None:
    if value is None:
        return None
    if type(value) is not str or value not in {"ACTIVE", "COMPLETED", "ARCHIVED"}:
        raise SavingsValidationError("status must be ACTIVE, COMPLETED, or ARCHIVED")
    return value  # type: ignore[return-value]


class SavingsService:
    def __init__(self, database: HouseholdDatabase) -> None:
        self._database = database

    def create_goal(
        self,
        name: object,
        target_amount_idr: object,
        description: object = None,
        target_date: object = None,
    ) -> SavingsGoalView:
        valid_name = _required_text(name, "name")
        valid_target = _positive_integer(target_amount_idr, "target_amount_idr")
        valid_description = _optional_text(description, "description")
        valid_date = _optional_date(target_date)
        self._database.initialize()
        goal_id = str(uuid4())
        now = utc_now()
        try:
            with self._database.connect() as connection:
                connection.execute(
                    """
                    INSERT INTO savings_goals (
                        id, name, description, target_amount_idr, target_date,
                        status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, 'ACTIVE', ?, ?)
                    """,
                    (goal_id, valid_name, valid_description, valid_target, valid_date, now, now),
                )
        except sqlite3.IntegrityError as error:
            raise SavingsConflictError(
                f"an active or completed savings goal named {valid_name!r} already exists"
            ) from error
        return self.get_goal(goal_id)

    def list_goals(self, status: object = None) -> tuple[SavingsGoalView, ...]:
        valid_status = _status(status)
        self._database.initialize()
        query = "SELECT * FROM savings_goals"
        parameters: tuple[object, ...] = ()
        if valid_status is not None:
            query += " WHERE status = ?"
            parameters = (valid_status,)
        query += " ORDER BY rowid"
        with self._database.connect() as connection:
            rows = connection.execute(query, parameters).fetchall()
            return tuple(self._goal_from_row(connection, row) for row in rows)

    def get_goal(self, goal_id: object) -> SavingsGoalView:
        valid_goal_id = _canonical_uuid(goal_id, "goal_id")
        self._database.initialize()
        with self._database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM savings_goals WHERE id = ?", (valid_goal_id,)
            ).fetchone()
            if row is None:
                raise SavingsNotFoundError(f"savings goal {valid_goal_id} was not found")
            return self._goal_from_row(connection, row)

    def record_contribution(
        self,
        goal_id: object,
        amount_idr: object,
        source_allocation_reference: object = None,
        note: object = None,
    ) -> SavingsContributionResult:
        valid_goal_id = _canonical_uuid(goal_id, "goal_id")
        valid_amount = _positive_integer(amount_idr, "amount_idr")
        valid_reference = (
            None
            if source_allocation_reference is None
            else _canonical_uuid(source_allocation_reference, "source_allocation_reference")
        )
        valid_note = _optional_text(note, "note")
        self._database.initialize()

        with self._database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                goal_row = connection.execute(
                    "SELECT * FROM savings_goals WHERE id = ?", (valid_goal_id,)
                ).fetchone()
                if goal_row is None:
                    raise SavingsNotFoundError(f"savings goal {valid_goal_id} was not found")

                if valid_reference is not None:
                    allocation = connection.execute(
                        "SELECT status FROM monthly_allocations WHERE id = ?",
                        (valid_reference,),
                    ).fetchone()
                    if allocation is None or allocation["status"] != "CONFIRMED":
                        raise SavingsValidationError(
                            "source_allocation_reference must identify a confirmed allocation"
                        )
                    existing = connection.execute(
                        """
                        SELECT * FROM savings_contributions
                        WHERE goal_id = ? AND source_allocation_reference = ?
                        """,
                        (valid_goal_id, valid_reference),
                    ).fetchone()
                    if existing is not None:
                        if existing["amount_idr"] != valid_amount:
                            raise SavingsConflictError(
                                "linked contribution already exists with a different amount"
                            )
                        connection.commit()
                        return SavingsContributionResult(
                            contribution=self._contribution_from_row(existing),
                            goal=self._goal_from_row(connection, goal_row),
                        )

                contribution_id = str(uuid4())
                now = utc_now()
                connection.execute(
                    """
                    INSERT INTO savings_contributions (
                        id, goal_id, amount_idr, recorded_at,
                        source_allocation_reference, note
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        contribution_id,
                        valid_goal_id,
                        valid_amount,
                        now,
                        valid_reference,
                        valid_note,
                    ),
                )
                current_amount = connection.execute(
                    "SELECT COALESCE(SUM(amount_idr), 0) FROM savings_contributions WHERE goal_id = ?",
                    (valid_goal_id,),
                ).fetchone()[0]
                if current_amount >= goal_row["target_amount_idr"] and goal_row["status"] == "ACTIVE":
                    connection.execute(
                        "UPDATE savings_goals SET status = 'COMPLETED', updated_at = ? WHERE id = ?",
                        (now, valid_goal_id),
                    )
                connection.commit()
            except Exception:
                connection.rollback()
                raise

            contribution_row = connection.execute(
                "SELECT * FROM savings_contributions WHERE id = ?", (contribution_id,)
            ).fetchone()
            updated_goal_row = connection.execute(
                "SELECT * FROM savings_goals WHERE id = ?", (valid_goal_id,)
            ).fetchone()
            assert contribution_row is not None and updated_goal_row is not None
            return SavingsContributionResult(
                contribution=self._contribution_from_row(contribution_row),
                goal=self._goal_from_row(connection, updated_goal_row),
            )

    @staticmethod
    def _goal_from_row(connection: sqlite3.Connection, row: sqlite3.Row) -> SavingsGoalView:
        current_amount = connection.execute(
            "SELECT COALESCE(SUM(amount_idr), 0) FROM savings_contributions WHERE goal_id = ?",
            (row["id"],),
        ).fetchone()[0]
        return SavingsGoalView(
            goal_id=row["id"],
            name=row["name"],
            description=row["description"],
            target_amount_idr=row["target_amount_idr"],
            current_amount_idr=current_amount,
            target_date=row["target_date"],
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    @staticmethod
    def _contribution_from_row(row: sqlite3.Row) -> SavingsContributionView:
        return SavingsContributionView(
            contribution_id=row["id"],
            goal_id=row["goal_id"],
            amount_idr=row["amount_idr"],
            recorded_at=row["recorded_at"],
            source_allocation_reference=row["source_allocation_reference"],
            note=row["note"],
        )
