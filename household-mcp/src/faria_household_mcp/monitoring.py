from __future__ import annotations

from collections.abc import Callable
import sqlite3
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from faria_household_mcp.database import HouseholdDatabase, utc_now


Persona = Literal["FINANCE", "GIVING"]
ActivityStatus = Literal["SUCCEEDED", "FAILED"]
PersonaStatus = Literal["IDLE", "WORKING", "ERROR"]


class AgentActivityView(BaseModel):
    model_config = ConfigDict(frozen=True, alias_generator=to_camel, populate_by_name=True)

    activity_id: str
    persona: Persona
    activity_type: str
    status: ActivityStatus
    summary: str
    reference_type: str | None
    reference_id: str | None
    occurred_at: str


class PersonaStateView(BaseModel):
    model_config = ConfigDict(frozen=True, alias_generator=to_camel, populate_by_name=True)

    persona: Persona
    status: PersonaStatus
    current_task: str | None
    last_activity_at: str | None
    last_error_summary: str | None
    updated_at: str


class MonitoringService:
    """Best-effort operational metadata kept separate from household truth."""

    def __init__(
        self,
        database: HouseholdDatabase,
        clock: Callable[[], str] = utc_now,
    ) -> None:
        self._database = database
        self._clock = clock

    def mark_working(self, persona: Persona, current_task: str) -> None:
        now = self._clock()
        self._database.initialize()
        with self._database.connect() as connection:
            connection.execute(
                """
                UPDATE agent_persona_state
                SET status = 'WORKING', current_task = ?, last_error_summary = NULL,
                    updated_at = ?
                WHERE persona = ?
                """,
                (current_task, now, persona),
            )

    def record_success(
        self,
        persona: Persona,
        activity_type: str,
        summary: str,
        reference_type: str | None = None,
        reference_id: str | None = None,
    ) -> AgentActivityView:
        return self._record(
            persona,
            activity_type,
            "SUCCEEDED",
            summary,
            reference_type,
            reference_id,
        )

    def record_failure(
        self,
        persona: Persona,
        activity_type: str,
        summary: str,
        reference_type: str | None = None,
        reference_id: str | None = None,
    ) -> AgentActivityView:
        return self._record(
            persona,
            activity_type,
            "FAILED",
            summary,
            reference_type,
            reference_id,
        )

    def list_recent(self, limit: int = 20) -> tuple[AgentActivityView, ...]:
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ValueError("limit must be an integer between 1 and 100")
        self._database.initialize()
        with self._database.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM agent_activities
                ORDER BY occurred_at DESC, rowid DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return tuple(self._activity_from_row(row) for row in rows)

    def get_active_persona_states(self) -> tuple[PersonaStateView, ...]:
        self._database.initialize()
        with self._database.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM agent_persona_state
                ORDER BY CASE persona WHEN 'FINANCE' THEN 1 ELSE 2 END
                """
            ).fetchall()
        return tuple(
            PersonaStateView(
                persona=row["persona"],
                status=row["status"],
                current_task=row["current_task"],
                last_activity_at=row["last_activity_at"],
                last_error_summary=row["last_error_summary"],
                updated_at=row["updated_at"],
            )
            for row in rows
        )

    def _record(
        self,
        persona: Persona,
        activity_type: str,
        status: ActivityStatus,
        summary: str,
        reference_type: str | None,
        reference_id: str | None,
    ) -> AgentActivityView:
        now = self._clock()
        activity_id = str(uuid4())
        persona_status = "IDLE" if status == "SUCCEEDED" else "ERROR"
        last_error = None if status == "SUCCEEDED" else summary
        self._database.initialize()
        with self._database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                connection.execute(
                    """
                    INSERT INTO agent_activities (
                        id, persona, activity_type, status, summary,
                        reference_type, reference_id, occurred_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        activity_id,
                        persona,
                        activity_type,
                        status,
                        summary,
                        reference_type,
                        reference_id,
                        now,
                    ),
                )
                connection.execute(
                    """
                    UPDATE agent_persona_state
                    SET status = ?, current_task = NULL, last_activity_at = ?,
                        last_error_summary = ?, updated_at = ?
                    WHERE persona = ?
                    """,
                    (persona_status, now, last_error, now, persona),
                )
                connection.commit()
            except Exception:
                connection.rollback()
                raise
        return AgentActivityView(
            activity_id=activity_id,
            persona=persona,
            activity_type=activity_type,
            status=status,
            summary=summary,
            reference_type=reference_type,
            reference_id=reference_id,
            occurred_at=now,
        )

    @staticmethod
    def _activity_from_row(row: sqlite3.Row) -> AgentActivityView:
        return AgentActivityView(
            activity_id=row["id"],
            persona=row["persona"],
            activity_type=row["activity_type"],
            status=row["status"],
            summary=row["summary"],
            reference_type=row["reference_type"],
            reference_id=row["reference_id"],
            occurred_at=row["occurred_at"],
        )
