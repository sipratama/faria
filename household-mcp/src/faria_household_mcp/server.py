from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import TypeVar

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import StrictInt

from faria_household_mcp.allocation import (
    AllocationError,
    AllocationItemInput,
    AllocationView,
    MonthlyAllocationService,
    PeriodAllocationView,
)
from faria_household_mcp.database import HouseholdDatabase
from faria_household_mcp.financial_rules import (
    FinancialRulesError,
    FinancialRulesService,
    FinancialRulesView,
    ZakatCalculationView,
)
from faria_household_mcp.giving import GivingError, GivingRecordView, GivingService, GivingType
from faria_household_mcp.monitoring import MonitoringService, Persona
from faria_household_mcp.routines import (
    RoutineError,
    RoutineScheduleKind,
    RoutineService,
    RoutineView,
)
from faria_household_mcp.savings import (
    SavingsContributionResult,
    SavingsError,
    SavingsGoalStatus,
    SavingsGoalView,
    SavingsService,
)


_T = TypeVar("_T")

TOOL_NAMES = frozenset(
    {
        "monthly_allocation_get",
        "monthly_allocation_save_draft",
        "monthly_allocation_confirm",
        "monthly_allocation_discard_draft",
        "financial_rules_get",
        "zakat_calculate",
        "savings_goal_list",
        "savings_goal_create",
        "savings_goal_get",
        "savings_contribution_record",
        "giving_list",
        "giving_record",
        "routine_list",
        "routine_get",
        "routine_create",
        "routine_scheduler_link",
        "routine_complete",
        "routine_cancel",
    }
)


def _call_domain(operation: Callable[..., _T], *args: object) -> _T:
    try:
        return operation(*args)
    except (AllocationError, FinancialRulesError, SavingsError, GivingError, RoutineError) as error:
        raise ToolError(str(error)) from error


def _best_effort(operation: Callable[..., object], *args: object) -> None:
    try:
        operation(*args)
    except Exception:
        # Monitoring is secondary and must never change the outcome of household operations.
        pass


def _call_monitored(
    monitoring: MonitoringService,
    persona: Persona,
    task: str,
    activity_type: str,
    success_summary: Callable[[_T], str],
    reference: Callable[[_T], tuple[str, str] | None],
    operation: Callable[..., _T],
    *args: object,
) -> _T:
    _best_effort(monitoring.mark_working, persona, task)
    try:
        result = operation(*args)
    except (AllocationError, FinancialRulesError, SavingsError, GivingError, RoutineError) as error:
        _best_effort(
            monitoring.record_failure,
            persona,
            activity_type,
            f"{task} failed.",
        )
        raise ToolError(str(error)) from error
    except Exception:
        _best_effort(
            monitoring.record_failure,
            persona,
            activity_type,
            f"{task} failed.",
        )
        raise

    def record_monitoring_success() -> None:
        activity_reference = reference(result)
        reference_type, reference_id = activity_reference or (None, None)
        monitoring.record_success(
            persona,
            activity_type,
            success_summary(result),
            reference_type,
            reference_id,
        )

    _best_effort(record_monitoring_success)
    return result


def create_server(database_path: str | Path | None = None) -> MCPServer:
    database = HouseholdDatabase(database_path)
    allocation_service = MonthlyAllocationService(database)
    rules_service = FinancialRulesService(database)
    savings_service = SavingsService(database)
    giving_service = GivingService(database)
    routine_service = RoutineService(database)
    monitoring = MonitoringService(database)
    server = MCPServer(
        name="faria-household",
        title="FARIA Household",
        description="Deterministic and constrained FARIA household-domain tools.",
        instructions=(
            "Monthly allocations are plans, while savings contributions and giving records are "
            "actual history. The orchestration layer must establish explicit human confirmation "
            "before confirming an allocation, creating a savings goal, recording a savings "
            "contribution, recording giving, creating a routine, or cancelling a routine. "
            "Household routine state is authoritative in SQLite; scheduler jobs are delivery "
            "machinery and must re-check routine_get before sending a reminder."
        ),
        version="0.1.0",
    )

    @server.tool(name="monthly_allocation_get", structured_output=True)
    def monthly_allocation_get(period: str) -> PeriodAllocationView:
        """Get the current draft and confirmed allocation state for an explicit YYYY-MM period."""
        return _call_domain(allocation_service.get, period)

    @server.tool(name="monthly_allocation_save_draft", structured_output=True)
    def monthly_allocation_save_draft(
        period: str,
        income_idr: StrictInt,
        items: list[AllocationItemInput],
    ) -> AllocationView:
        """Create or update a non-authoritative draft from caller-supplied IDR values."""
        return _call_monitored(
            monitoring,
            "FINANCE",
            "Monthly allocation draft",
            "MONTHLY_ALLOCATION_DRAFT_SAVED",
            lambda result: f"Monthly allocation draft saved for {result.period}.",
            lambda result: ("MONTHLY_ALLOCATION", result.allocation_id),
            allocation_service.save_draft,
            period,
            income_idr,
            items,
        )

    @server.tool(name="monthly_allocation_confirm", structured_output=True)
    def monthly_allocation_confirm(
        allocation_id: str,
        confirmation_reference: str | None = None,
    ) -> AllocationView:
        """Make an existing draft authoritative after external human confirmation."""
        return _call_monitored(
            monitoring,
            "FINANCE",
            "Monthly allocation confirmation",
            "MONTHLY_ALLOCATION_CONFIRMED",
            lambda result: f"Monthly allocation confirmed for {result.period}.",
            lambda result: ("MONTHLY_ALLOCATION", result.allocation_id),
            allocation_service.confirm,
            allocation_id,
            confirmation_reference,
        )

    @server.tool(name="monthly_allocation_discard_draft", structured_output=True)
    def monthly_allocation_discard_draft(allocation_id: str) -> AllocationView:
        """Discard an existing draft; confirmed allocations cannot be discarded."""
        return _call_monitored(
            monitoring,
            "FINANCE",
            "Monthly allocation draft discard",
            "MONTHLY_ALLOCATION_DRAFT_DISCARDED",
            lambda result: f"Monthly allocation draft discarded for {result.period}.",
            lambda result: ("MONTHLY_ALLOCATION", result.allocation_id),
            allocation_service.discard_draft,
            allocation_id,
        )

    @server.tool(name="financial_rules_get", structured_output=True)
    def financial_rules_get() -> FinancialRulesView:
        """Get the authoritative household-selected finance rules."""
        return _call_domain(rules_service.get)

    @server.tool(name="zakat_calculate", structured_output=True)
    def zakat_calculate(thp_idr: StrictInt) -> ZakatCalculationView:
        """Calculate zakat from THP using the authoritative household-selected rule."""
        return _call_domain(rules_service.calculate_zakat, thp_idr)

    @server.tool(name="savings_goal_list", structured_output=True)
    def savings_goal_list(status: SavingsGoalStatus | None = None) -> tuple[SavingsGoalView, ...]:
        """List savings goals and their contribution-derived progress."""
        return _call_domain(savings_service.list_goals, status)

    @server.tool(name="savings_goal_create", structured_output=True)
    def savings_goal_create(
        name: str,
        target_amount_idr: StrictInt,
        description: str | None = None,
        target_date: str | None = None,
    ) -> SavingsGoalView:
        """Create a goal only after the orchestration layer obtains explicit confirmation."""
        return _call_monitored(
            monitoring,
            "FINANCE",
            "Savings goal creation",
            "SAVINGS_GOAL_CREATED",
            lambda result: "Savings goal created.",
            lambda result: ("SAVINGS_GOAL", result.goal_id),
            savings_service.create_goal,
            name,
            target_amount_idr,
            description,
            target_date,
        )

    @server.tool(name="savings_goal_get", structured_output=True)
    def savings_goal_get(goal_id: str) -> SavingsGoalView:
        """Get one savings goal and its authoritative contribution-derived progress."""
        return _call_domain(savings_service.get_goal, goal_id)

    @server.tool(name="savings_contribution_record", structured_output=True)
    def savings_contribution_record(
        goal_id: str,
        amount_idr: StrictInt,
        source_allocation_reference: str | None = None,
        note: str | None = None,
    ) -> SavingsContributionResult:
        """Record actual savings progress only after explicit human confirmation."""
        return _call_monitored(
            monitoring,
            "FINANCE",
            "Savings contribution recording",
            "SAVINGS_CONTRIBUTION_RECORDED",
            lambda result: "Savings contribution recorded.",
            lambda result: ("SAVINGS_CONTRIBUTION", result.contribution.contribution_id),
            savings_service.record_contribution,
            goal_id,
            amount_idr,
            source_allocation_reference,
            note,
        )

    @server.tool(name="giving_list", structured_output=True)
    def giving_list(
        period: str | None = None,
        type: GivingType | None = None,
    ) -> tuple[GivingRecordView, ...]:
        """List immutable actual giving records, optionally filtered by period and type."""
        return _call_domain(giving_service.list_records, period, type)

    @server.tool(name="giving_record", structured_output=True)
    def giving_record(
        type: GivingType,
        amount_idr: StrictInt,
        period: str,
        monthly_allocation_reference: str | None = None,
        note: str | None = None,
    ) -> GivingRecordView:
        """Record actual giving only after the orchestration layer obtains explicit confirmation."""
        return _call_monitored(
            monitoring,
            "GIVING",
            "Giving record creation",
            "GIVING_RECORDED",
            lambda result: (
                "Zakat giving recorded."
                if result.type == "zakat_penghasilan"
                else "Sedekah giving recorded."
            ),
            lambda result: ("GIVING_RECORD", result.giving_record_id),
            giving_service.record,
            type,
            amount_idr,
            period,
            monthly_allocation_reference,
            note,
        )

    @server.tool(name="routine_list", structured_output=True)
    def routine_list(include_inactive: bool = False) -> tuple[RoutineView, ...]:
        """List open routines by default, or include completed/cancelled history."""
        return _call_domain(routine_service.list, include_inactive)

    @server.tool(name="routine_get", structured_output=True)
    def routine_get(routine_id: str) -> RoutineView:
        """Get one authoritative household routine, including scheduler linkage and due time."""
        return _call_domain(routine_service.get, routine_id)

    @server.tool(name="routine_create", structured_output=True)
    def routine_create(
        title: str,
        schedule_kind: RoutineScheduleKind,
        schedule_expression: str,
        timezone: str,
        description: str | None = None,
    ) -> RoutineView:
        """Create PENDING_SCHEDULE state only after explicit human confirmation."""
        return _call_monitored(
            monitoring,
            "HOME_OPS",
            "Household routine creation",
            "HOUSEHOLD_ROUTINE_CREATED",
            lambda result: "Household routine created pending scheduling.",
            lambda result: ("HOUSEHOLD_ROUTINE", result.routine_id),
            routine_service.create,
            title,
            schedule_kind,
            schedule_expression,
            timezone,
            description,
        )

    @server.tool(name="routine_scheduler_link", structured_output=True)
    def routine_scheduler_link(routine_id: str, scheduler_job_id: str) -> RoutineView:
        """Atomically bind a successfully created Hermes job and activate its routine."""
        return _call_monitored(
            monitoring,
            "HOME_OPS",
            "Household routine scheduler linking",
            "HOUSEHOLD_ROUTINE_SCHEDULER_LINKED",
            lambda result: "Household routine scheduler linked and activated.",
            lambda result: ("HOUSEHOLD_ROUTINE", result.routine_id),
            routine_service.link_scheduler,
            routine_id,
            scheduler_job_id,
        )

    @server.tool(name="routine_complete", structured_output=True)
    def routine_complete(routine_id: str) -> RoutineView:
        """Complete a one-off routine or only the current recurring occurrence."""
        return _call_monitored(
            monitoring,
            "HOME_OPS",
            "Household routine completion",
            "HOUSEHOLD_ROUTINE_COMPLETED",
            lambda result: (
                "One-off household routine completed."
                if result.status == "COMPLETED"
                else "Recurring household routine occurrence completed."
            ),
            lambda result: ("HOUSEHOLD_ROUTINE", result.routine_id),
            routine_service.complete,
            routine_id,
        )

    @server.tool(name="routine_cancel", structured_output=True)
    def routine_cancel(routine_id: str) -> RoutineView:
        """Authoritatively cancel future reminder delivery without deleting history."""
        return _call_monitored(
            monitoring,
            "HOME_OPS",
            "Household routine cancellation",
            "HOUSEHOLD_ROUTINE_CANCELLED",
            lambda result: "Household routine cancelled.",
            lambda result: ("HOUSEHOLD_ROUTINE", result.routine_id),
            routine_service.cancel,
            routine_id,
        )

    return server


def main() -> None:
    create_server().run(transport="stdio")


if __name__ == "__main__":
    main()
