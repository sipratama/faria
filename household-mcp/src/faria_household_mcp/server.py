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
    }
)


def _call_domain(operation: Callable[..., _T], *args: object) -> _T:
    try:
        return operation(*args)
    except (AllocationError, FinancialRulesError, SavingsError, GivingError) as error:
        raise ToolError(str(error)) from error


def create_server(database_path: str | Path | None = None) -> MCPServer:
    database = HouseholdDatabase(database_path)
    allocation_service = MonthlyAllocationService(database)
    rules_service = FinancialRulesService(database)
    savings_service = SavingsService(database)
    giving_service = GivingService(database)
    server = MCPServer(
        name="faria-household",
        title="FARIA Household",
        description="Deterministic and constrained FARIA household-domain tools.",
        instructions=(
            "Monthly allocations are plans, while savings contributions and giving records are "
            "actual history. The orchestration layer must establish explicit human confirmation "
            "before confirming an allocation, creating a savings goal, recording a savings "
            "contribution, or recording giving."
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
        return _call_domain(allocation_service.save_draft, period, income_idr, items)

    @server.tool(name="monthly_allocation_confirm", structured_output=True)
    def monthly_allocation_confirm(
        allocation_id: str,
        confirmation_reference: str | None = None,
    ) -> AllocationView:
        """Make an existing draft authoritative after external human confirmation."""
        return _call_domain(allocation_service.confirm, allocation_id, confirmation_reference)

    @server.tool(name="monthly_allocation_discard_draft", structured_output=True)
    def monthly_allocation_discard_draft(allocation_id: str) -> AllocationView:
        """Discard an existing draft; confirmed allocations cannot be discarded."""
        return _call_domain(allocation_service.discard_draft, allocation_id)

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
        return _call_domain(
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
        return _call_domain(
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
        return _call_domain(
            giving_service.record,
            type,
            amount_idr,
            period,
            monthly_allocation_reference,
            note,
        )

    return server


def main() -> None:
    create_server().run(transport="stdio")


if __name__ == "__main__":
    main()
