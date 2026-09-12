from __future__ import annotations

import sqlite3
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Literal
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from croniter import CroniterBadCronError, CroniterBadDateError, croniter
from pydantic import BaseModel, ConfigDict

from faria_household_mcp.database import HouseholdDatabase

HOUSEHOLD_TIMEZONE_NAME = "Asia/Jakarta"
HOUSEHOLD_TIMEZONE = ZoneInfo(HOUSEHOLD_TIMEZONE_NAME)

RoutineScheduleKind = Literal["ONE_OFF", "RECURRING"]
RoutineStatus = Literal["PENDING_SCHEDULE", "ACTIVE", "COMPLETED", "CANCELLED"]


class RoutineError(Exception):
    """Base exception for household routine operations."""


class RoutineValidationError(RoutineError):
    """Raised when routine input is invalid."""


class RoutineNotFoundError(RoutineError):
    """Raised when a routine does not exist."""


class RoutineConflictError(RoutineError):
    """Raised when a routine transition conflicts with authoritative state."""


class RoutineView(BaseModel):
    model_config = ConfigDict(frozen=True)

    routine_id: str
    title: str
    description: str | None
    schedule_kind: RoutineScheduleKind
    schedule_expression: str
    timezone: Literal["Asia/Jakarta"]
    status: RoutineStatus
    scheduler_job_id: str | None
    next_due_at: str | None
    last_completed_at: str | None
    created_at: str
    updated_at: str


def _required_text(value: object, field: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RoutineValidationError(f"{field} is required")
    normalized = value.strip()
    if len(normalized) > maximum:
        raise RoutineValidationError(f"{field} must be at most {maximum} characters")
    return normalized


def _optional_text(value: object, field: str, maximum: int) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise RoutineValidationError(f"{field} must be text")
    normalized = value.strip()
    if not normalized:
        return None
    if len(normalized) > maximum:
        raise RoutineValidationError(f"{field} must be at most {maximum} characters")
    return normalized


def _canonical_uuid(value: object) -> str:
    if not isinstance(value, str):
        raise RoutineValidationError("routine_id must be a UUID")
    try:
        parsed = UUID(value)
    except (ValueError, AttributeError) as error:
        raise RoutineValidationError("routine_id must be a UUID") from error
    if str(parsed) != value:
        raise RoutineValidationError("routine_id must use canonical UUID format")
    return value


def _schedule_kind(value: object) -> RoutineScheduleKind:
    if value not in ("ONE_OFF", "RECURRING"):
        raise RoutineValidationError("schedule_kind must be ONE_OFF or RECURRING")
    return value


def _timezone(value: object) -> Literal["Asia/Jakarta"]:
    if value != HOUSEHOLD_TIMEZONE_NAME:
        raise RoutineValidationError("timezone must be Asia/Jakarta")
    try:
        ZoneInfo(str(value))
    except ZoneInfoNotFoundError as error:
        raise RoutineValidationError("timezone is not available") from error
    return HOUSEHOLD_TIMEZONE_NAME


def _aware_now(clock: Callable[[], datetime]) -> datetime:
    now = clock()
    if now.tzinfo is None or now.utcoffset() is None:
        raise RuntimeError("routine clock must return an offset-aware datetime")
    return now


def _utc_timestamp(value: datetime) -> str:
    return value.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _one_off_schedule(value: object, now: datetime) -> str:
    expression = _required_text(value, "schedule_expression", 120)
    try:
        scheduled = datetime.fromisoformat(expression.replace("Z", "+00:00"))
    except ValueError as error:
        raise RoutineValidationError(
            "ONE_OFF schedule_expression must be an offset-aware ISO timestamp"
        ) from error
    if scheduled.tzinfo is None or scheduled.utcoffset() is None:
        raise RoutineValidationError(
            "ONE_OFF schedule_expression must be an offset-aware ISO timestamp"
        )
    if scheduled.utcoffset() != scheduled.astimezone(HOUSEHOLD_TIMEZONE).utcoffset():
        raise RoutineValidationError("ONE_OFF schedule_expression must use Asia/Jakarta offset")
    if scheduled <= now.astimezone(scheduled.tzinfo):
        raise RoutineValidationError("ONE_OFF schedule_expression must be in the future")
    return scheduled.isoformat(timespec="seconds")


def _recurring_schedule(value: object) -> str:
    expression = _required_text(value, "schedule_expression", 120)
    fields = expression.split()
    if len(fields) != 5:
        raise RoutineValidationError("RECURRING schedule_expression must have exactly 5 fields")
    canonical = " ".join(fields)
    try:
        croniter(canonical, datetime(2099, 1, 1, tzinfo=HOUSEHOLD_TIMEZONE)).get_next(
            datetime
        )
    except (CroniterBadCronError, CroniterBadDateError, ValueError, KeyError) as error:
        raise RoutineValidationError("RECURRING schedule_expression is invalid") from error
    return canonical


def _scheduler_job_id(value: object) -> str:
    return _required_text(value, "scheduler_job_id", 160)


class RoutineService:
    def __init__(
        self,
        database: HouseholdDatabase,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._database = database
        self._clock = clock or (lambda: datetime.now(UTC))

    def create(
        self,
        title: object,
        schedule_kind: object,
        schedule_expression: object,
        timezone: object,
        description: object = None,
    ) -> RoutineView:
        normalized_title = _required_text(title, "title", 120)
        normalized_description = _optional_text(description, "description", 500)
        normalized_kind = _schedule_kind(schedule_kind)
        normalized_timezone = _timezone(timezone)
        now = _aware_now(self._clock)
        if normalized_kind == "ONE_OFF":
            normalized_schedule = _one_off_schedule(schedule_expression, now)
        else:
            normalized_schedule = _recurring_schedule(schedule_expression)
        timestamp = _utc_timestamp(now)
        routine_id = str(uuid4())

        self._database.initialize()
        with self._database.connect() as connection:
            connection.execute(
                """
                INSERT INTO household_routines (
                    id, title, description, schedule_kind, schedule_expression,
                    timezone, status, scheduler_job_id, last_completed_at,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, 'PENDING_SCHEDULE', NULL, NULL, ?, ?)
                """,
                (
                    routine_id,
                    normalized_title,
                    normalized_description,
                    normalized_kind,
                    normalized_schedule,
                    normalized_timezone,
                    timestamp,
                    timestamp,
                ),
            )
            row = connection.execute(
                "SELECT * FROM household_routines WHERE id = ?", (routine_id,)
            ).fetchone()
        return self._from_row(row, now)

    def list(self, include_inactive: object = False) -> tuple[RoutineView, ...]:
        if type(include_inactive) is not bool:
            raise RoutineValidationError("include_inactive must be a boolean")
        now = _aware_now(self._clock)
        self._database.initialize()
        with self._database.connect() as connection:
            if include_inactive:
                rows = connection.execute("SELECT * FROM household_routines").fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT * FROM household_routines
                    WHERE status IN ('PENDING_SCHEDULE', 'ACTIVE')
                    """
                ).fetchall()
        routines = [self._from_row(row, now) for row in rows]
        routines.sort(
            key=lambda routine: (
                routine.next_due_at is None,
                routine.next_due_at or "",
                routine.created_at,
                routine.routine_id,
            )
        )
        return tuple(routines)

    def get(self, routine_id: object) -> RoutineView:
        normalized_id = _canonical_uuid(routine_id)
        now = _aware_now(self._clock)
        self._database.initialize()
        with self._database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM household_routines WHERE id = ?", (normalized_id,)
            ).fetchone()
        if row is None:
            raise RoutineNotFoundError("routine not found")
        return self._from_row(row, now)

    def link_scheduler(self, routine_id: object, scheduler_job_id: object) -> RoutineView:
        normalized_id = _canonical_uuid(routine_id)
        normalized_job_id = _scheduler_job_id(scheduler_job_id)
        now = _aware_now(self._clock)
        timestamp = _utc_timestamp(now)
        self._database.initialize()
        with self._database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                row = connection.execute(
                    "SELECT * FROM household_routines WHERE id = ?", (normalized_id,)
                ).fetchone()
                if row is None:
                    raise RoutineNotFoundError("routine not found")
                if row["status"] == "ACTIVE" and row["scheduler_job_id"] == normalized_job_id:
                    connection.commit()
                    return self._from_row(row, now)
                if row["status"] != "PENDING_SCHEDULE":
                    raise RoutineConflictError(
                        f"routine cannot be scheduler-linked from {row['status']}"
                    )
                if row["scheduler_job_id"] not in (None, normalized_job_id):
                    raise RoutineConflictError("routine already has a different scheduler job")
                try:
                    connection.execute(
                        """
                        UPDATE household_routines
                        SET status = 'ACTIVE', scheduler_job_id = ?, updated_at = ?
                        WHERE id = ? AND status = 'PENDING_SCHEDULE'
                        """,
                        (normalized_job_id, timestamp, normalized_id),
                    )
                except sqlite3.IntegrityError as error:
                    raise RoutineConflictError("scheduler job is already linked") from error
                updated = connection.execute(
                    "SELECT * FROM household_routines WHERE id = ?", (normalized_id,)
                ).fetchone()
                connection.commit()
            except Exception:
                connection.rollback()
                raise
        return self._from_row(updated, now)

    def complete(self, routine_id: object) -> RoutineView:
        normalized_id = _canonical_uuid(routine_id)
        now = _aware_now(self._clock)
        timestamp = _utc_timestamp(now)
        self._database.initialize()
        with self._database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                row = connection.execute(
                    "SELECT * FROM household_routines WHERE id = ?", (normalized_id,)
                ).fetchone()
                if row is None:
                    raise RoutineNotFoundError("routine not found")
                if row["status"] != "ACTIVE":
                    raise RoutineConflictError(f"routine cannot be completed from {row['status']}")
                next_status = "COMPLETED" if row["schedule_kind"] == "ONE_OFF" else "ACTIVE"
                connection.execute(
                    """
                    UPDATE household_routines
                    SET status = ?, last_completed_at = ?, updated_at = ?
                    WHERE id = ? AND status = 'ACTIVE'
                    """,
                    (next_status, timestamp, timestamp, normalized_id),
                )
                updated = connection.execute(
                    "SELECT * FROM household_routines WHERE id = ?", (normalized_id,)
                ).fetchone()
                connection.commit()
            except Exception:
                connection.rollback()
                raise
        return self._from_row(updated, now)

    def cancel(self, routine_id: object) -> RoutineView:
        normalized_id = _canonical_uuid(routine_id)
        now = _aware_now(self._clock)
        timestamp = _utc_timestamp(now)
        self._database.initialize()
        with self._database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                row = connection.execute(
                    "SELECT * FROM household_routines WHERE id = ?", (normalized_id,)
                ).fetchone()
                if row is None:
                    raise RoutineNotFoundError("routine not found")
                if row["status"] == "CANCELLED":
                    connection.commit()
                    return self._from_row(row, now)
                if row["status"] not in ("PENDING_SCHEDULE", "ACTIVE"):
                    raise RoutineConflictError(f"routine cannot be cancelled from {row['status']}")
                connection.execute(
                    """
                    UPDATE household_routines
                    SET status = 'CANCELLED', updated_at = ?
                    WHERE id = ? AND status IN ('PENDING_SCHEDULE', 'ACTIVE')
                    """,
                    (timestamp, normalized_id),
                )
                updated = connection.execute(
                    "SELECT * FROM household_routines WHERE id = ?", (normalized_id,)
                ).fetchone()
                connection.commit()
            except Exception:
                connection.rollback()
                raise
        return self._from_row(updated, now)

    @staticmethod
    def _next_due_at(row: sqlite3.Row, now: datetime) -> str | None:
        if row["status"] != "ACTIVE":
            return None
        if row["schedule_kind"] == "ONE_OFF":
            return row["schedule_expression"]
        next_due = croniter(
            row["schedule_expression"], now.astimezone(HOUSEHOLD_TIMEZONE)
        ).get_next(datetime)
        return next_due.isoformat(timespec="seconds")

    @classmethod
    def _from_row(cls, row: sqlite3.Row, now: datetime) -> RoutineView:
        return RoutineView(
            routine_id=row["id"],
            title=row["title"],
            description=row["description"],
            schedule_kind=row["schedule_kind"],
            schedule_expression=row["schedule_expression"],
            timezone=row["timezone"],
            status=row["status"],
            scheduler_job_id=row["scheduler_job_id"],
            next_due_at=cls._next_due_at(row, now),
            last_completed_at=row["last_completed_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
