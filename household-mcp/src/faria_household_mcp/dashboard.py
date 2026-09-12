from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Literal
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from faria_household_mcp.database import HouseholdDatabase
from faria_household_mcp.monitoring import AgentActivityView, MonitoringService


HOUSEHOLD_TIMEZONE = ZoneInfo("Asia/Jakarta")


class DashboardModel(BaseModel):
    model_config = ConfigDict(frozen=True, alias_generator=to_camel, populate_by_name=True)


class FariaHealthView(DashboardModel):
    status: Literal["healthy", "working", "attention"]
    model_alias: str
    dashboard_api: Literal["healthy"]
    database: Literal["healthy"]
    gateway: Literal["not_monitored"]
    router: Literal["not_monitored"]
    usage_monitoring: Literal["not_connected"]


class DashboardPersonaView(DashboardModel):
    persona: Literal["FINANCE", "GIVING", "HOME_OPS", "PLANNER"]
    label: str
    activated: bool
    status: Literal["IDLE", "WORKING", "ERROR", "NOT_ACTIVATED"]
    current_task: str | None
    last_activity_at: str | None
    last_error_summary: str | None


class PendingConfirmationView(DashboardModel):
    type: Literal["MONTHLY_ALLOCATION"]
    reference_id: str
    period: str
    summary: str
    created_at: str


class MonthlyAllocationSnapshot(DashboardModel):
    latest_confirmed_period: str | None
    status: Literal["CONFIRMED"] | None
    remainder_idr: int | None


class SavingsSnapshot(DashboardModel):
    active_goal_count: int
    completed_goal_count: int


class GivingSnapshot(DashboardModel):
    current_period: str
    current_period_count: int
    latest_type: Literal["zakat_penghasilan", "sedekah"] | None
    latest_period: str | None
    latest_recorded_at: str | None


class HouseholdSnapshot(DashboardModel):
    monthly_allocation: MonthlyAllocationSnapshot
    savings: SavingsSnapshot
    giving: GivingSnapshot


class DashboardSnapshot(DashboardModel):
    faria: FariaHealthView
    personas: tuple[DashboardPersonaView, ...]
    pending_confirmations: tuple[PendingConfirmationView, ...]
    household_snapshot: HouseholdSnapshot
    recent_activities: tuple[AgentActivityView, ...]
    generated_at: str


class ActivitiesResponse(DashboardModel):
    activities: tuple[AgentActivityView, ...]
    generated_at: str


class DashboardQueryService:
    def __init__(
        self,
        database: HouseholdDatabase,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._database = database
        self._monitoring = MonitoringService(database)
        self._clock = clock or (lambda: datetime.now(UTC))

    def health(self) -> None:
        self._database.initialize()
        with self._database.connect() as connection:
            connection.execute("SELECT 1").fetchone()

    def get_dashboard(self) -> DashboardSnapshot:
        now = self._clock()
        generated_at = now.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
        current_period = now.astimezone(HOUSEHOLD_TIMEZONE).strftime("%Y-%m")
        states = self._monitoring.get_active_persona_states()
        state_by_persona = {state.persona: state for state in states}

        with self._database.connect() as connection:
            pending_rows = connection.execute(
                """
                SELECT id, period, created_at
                FROM monthly_allocations
                WHERE status = 'DRAFT'
                ORDER BY period DESC, created_at DESC
                """
            ).fetchall()
            confirmed = connection.execute(
                """
                SELECT id, period, income_idr
                FROM monthly_allocations
                WHERE status = 'CONFIRMED'
                ORDER BY period DESC, confirmed_at DESC
                LIMIT 1
                """
            ).fetchone()
            allocation_total = 0
            if confirmed is not None:
                allocation_total = connection.execute(
                    "SELECT COALESCE(SUM(amount_idr), 0) FROM allocation_items WHERE allocation_id = ?",
                    (confirmed["id"],),
                ).fetchone()[0]
            savings_counts = connection.execute(
                """
                SELECT
                    SUM(CASE WHEN status = 'ACTIVE' THEN 1 ELSE 0 END) AS active_count,
                    SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) AS completed_count
                FROM savings_goals
                """
            ).fetchone()
            current_giving_count = connection.execute(
                "SELECT COUNT(*) FROM giving_records WHERE period = ?",
                (current_period,),
            ).fetchone()[0]
            latest_giving = connection.execute(
                """
                SELECT type, period, recorded_at
                FROM giving_records
                ORDER BY recorded_at DESC, rowid DESC
                LIMIT 1
                """
            ).fetchone()

        personas = tuple(
            self._active_persona(persona, label, state_by_persona[persona])
            for persona, label in (("FINANCE", "Finance"), ("GIVING", "Giving"))
        ) + (
            self._inactive_persona("HOME_OPS", "Home Ops"),
            self._inactive_persona("PLANNER", "Planner"),
        )
        if any(persona.status == "ERROR" for persona in personas if persona.activated):
            overall_status = "attention"
        elif any(persona.status == "WORKING" for persona in personas if persona.activated):
            overall_status = "working"
        else:
            overall_status = "healthy"

        return DashboardSnapshot(
            faria=FariaHealthView(
                status=overall_status,
                model_alias="faria-household-main",
                dashboard_api="healthy",
                database="healthy",
                gateway="not_monitored",
                router="not_monitored",
                usage_monitoring="not_connected",
            ),
            personas=personas,
            pending_confirmations=tuple(
                PendingConfirmationView(
                    type="MONTHLY_ALLOCATION",
                    reference_id=row["id"],
                    period=row["period"],
                    summary=f"Monthly allocation {row['period']} waiting for confirmation.",
                    created_at=row["created_at"],
                )
                for row in pending_rows
            ),
            household_snapshot=HouseholdSnapshot(
                monthly_allocation=MonthlyAllocationSnapshot(
                    latest_confirmed_period=None if confirmed is None else confirmed["period"],
                    status=None if confirmed is None else "CONFIRMED",
                    remainder_idr=(
                        None
                        if confirmed is None
                        else confirmed["income_idr"] - allocation_total
                    ),
                ),
                savings=SavingsSnapshot(
                    active_goal_count=savings_counts["active_count"] or 0,
                    completed_goal_count=savings_counts["completed_count"] or 0,
                ),
                giving=GivingSnapshot(
                    current_period=current_period,
                    current_period_count=current_giving_count,
                    latest_type=None if latest_giving is None else latest_giving["type"],
                    latest_period=None if latest_giving is None else latest_giving["period"],
                    latest_recorded_at=(
                        None if latest_giving is None else latest_giving["recorded_at"]
                    ),
                ),
            ),
            recent_activities=self._monitoring.list_recent(20),
            generated_at=generated_at,
        )

    def get_activities(self) -> ActivitiesResponse:
        now = self._clock()
        return ActivitiesResponse(
            activities=self._monitoring.list_recent(20),
            generated_at=now.astimezone(UTC)
            .isoformat(timespec="seconds")
            .replace("+00:00", "Z"),
        )

    @staticmethod
    def _active_persona(persona: str, label: str, state: object) -> DashboardPersonaView:
        return DashboardPersonaView(
            persona=persona,
            label=label,
            activated=True,
            status=state.status,
            current_task=state.current_task,
            last_activity_at=state.last_activity_at,
            last_error_summary=state.last_error_summary,
        )

    @staticmethod
    def _inactive_persona(persona: str, label: str) -> DashboardPersonaView:
        return DashboardPersonaView(
            persona=persona,
            label=label,
            activated=False,
            status="NOT_ACTIVATED",
            current_task=None,
            last_activity_at=None,
            last_error_summary=None,
        )
