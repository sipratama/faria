from __future__ import annotations

from datetime import UTC, datetime

from faria_household_mcp.allocation import MonthlyAllocationService
from faria_household_mcp.dashboard import DashboardQueryService
from faria_household_mcp.database import HouseholdDatabase
from faria_household_mcp.giving import GivingService
from faria_household_mcp.monitoring import MonitoringService
from faria_household_mcp.routines import RoutineService
from faria_household_mcp.savings import SavingsService


NOW = datetime(2099, 1, 15, 8, 30, tzinfo=UTC)


def test_empty_dashboard_reports_only_observable_state(tmp_path) -> None:
    dashboard = DashboardQueryService(
        HouseholdDatabase(tmp_path / "faria.db"), clock=lambda: NOW
    ).get_dashboard()

    assert dashboard.faria.status == "healthy"
    assert dashboard.faria.gateway == "not_monitored"
    assert dashboard.faria.router == "not_monitored"
    assert dashboard.faria.usage_monitoring == "not_connected"
    assert [(persona.persona, persona.activated, persona.status) for persona in dashboard.personas] == [
        ("FINANCE", True, "IDLE"),
        ("GIVING", True, "IDLE"),
        ("HOME_OPS", True, "IDLE"),
        ("PLANNER", False, "NOT_ACTIVATED"),
    ]
    assert dashboard.pending_confirmations == ()
    assert dashboard.recent_activities == ()
    assert dashboard.household_snapshot.monthly_allocation.latest_confirmed_period is None
    assert dashboard.household_snapshot.savings.active_goal_count == 0
    assert dashboard.household_snapshot.giving.current_period_count == 0
    assert dashboard.household_snapshot.home_ops.active_routine_count == 0
    assert dashboard.household_snapshot.home_ops.next_routine is None


def test_dashboard_uses_authoritative_household_data_and_draft_confirmation(tmp_path) -> None:
    database = HouseholdDatabase(tmp_path / "faria.db")
    allocations = MonthlyAllocationService(database)
    savings = SavingsService(database)
    giving = GivingService(database)
    confirmed_draft = allocations.save_draft(
        "2098-12", 1_000_000, [{"category": "buffer", "amount_idr": 250_000}]
    )
    allocations.confirm(confirmed_draft.allocation_id, "synthetic-test")
    pending = allocations.save_draft("2099-01", 2_000_000, [])
    active_goal = savings.create_goal("Synthetic active", 500_000)
    completed_goal = savings.create_goal("Synthetic complete", 100_000)
    savings.record_contribution(completed_goal.goal_id, 100_000)
    giving.record("sedekah", 10_000, "2099-01")
    MonitoringService(database, clock=lambda: "2099-01-15T08:00:00Z").record_success(
        "GIVING", "GIVING_RECORDED", "Sedekah giving recorded."
    )

    dashboard = DashboardQueryService(database, clock=lambda: NOW).get_dashboard()

    assert dashboard.pending_confirmations[0].reference_id == pending.allocation_id
    assert dashboard.pending_confirmations[0].period == "2099-01"
    assert dashboard.household_snapshot.monthly_allocation.latest_confirmed_period == "2098-12"
    assert dashboard.household_snapshot.monthly_allocation.remainder_idr == 750_000
    assert dashboard.household_snapshot.savings.active_goal_count == 1
    assert dashboard.household_snapshot.savings.completed_goal_count == 1
    assert dashboard.household_snapshot.giving.current_period_count == 1
    assert dashboard.household_snapshot.giving.latest_type == "sedekah"
    assert dashboard.recent_activities[0].summary == "Sedekah giving recorded."
    assert active_goal.status == "ACTIVE"


def test_dashboard_projects_next_active_routine_from_sqlite(tmp_path) -> None:
    database = HouseholdDatabase(tmp_path / "faria.db")
    routines = RoutineService(database, clock=lambda: NOW)
    later = routines.create(
        "Synthetic quarterly check", "RECURRING", "0 10 1 */3 *", "Asia/Jakarta"
    )
    next_routine = routines.create(
        "Synthetic gallon check",
        "ONE_OFF",
        "2099-01-15T19:00:00+07:00",
        "Asia/Jakarta",
    )
    cancelled = routines.create(
        "Synthetic cancelled", "RECURRING", "0 9 * * *", "Asia/Jakarta"
    )
    routines.link_scheduler(later.routine_id, "cron-later")
    routines.link_scheduler(next_routine.routine_id, "cron-next")
    routines.link_scheduler(cancelled.routine_id, "cron-cancelled")
    routines.cancel(cancelled.routine_id)

    dashboard = DashboardQueryService(database, clock=lambda: NOW).get_dashboard()
    home_ops = dashboard.household_snapshot.home_ops

    assert home_ops.active_routine_count == 2
    assert home_ops.next_routine is not None
    assert home_ops.next_routine.routine_id == next_routine.routine_id
    assert home_ops.next_routine.title == "Synthetic gallon check"
    assert home_ops.next_routine.next_due_at == "2099-01-15T19:00:00+07:00"
    assert dashboard.personas[2].persona == "HOME_OPS"
    assert dashboard.personas[2].activated is True
    assert dashboard.personas[3].persona == "PLANNER"
    assert dashboard.personas[3].activated is False
