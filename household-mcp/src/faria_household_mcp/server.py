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


_T = TypeVar("_T")

TOOL_NAMES = frozenset(
    {
        "monthly_allocation_get",
        "monthly_allocation_save_draft",
        "monthly_allocation_confirm",
        "monthly_allocation_discard_draft",
    }
)


def _call_domain(operation: Callable[..., _T], *args: object) -> _T:
    try:
        return operation(*args)
    except AllocationError as error:
        raise ToolError(str(error)) from error


def create_server(database_path: str | Path | None = None) -> MCPServer:
    service = MonthlyAllocationService(HouseholdDatabase(database_path))
    server = MCPServer(
        name="faria-household",
        title="FARIA Household",
        description="Deterministic and constrained FARIA household-domain tools.",
        instructions=(
            "Draft allocations are non-authoritative. Call monthly_allocation_confirm only after "
            "the orchestration layer has established explicit human confirmation."
        ),
        version="0.1.0",
    )

    @server.tool(name="monthly_allocation_get", structured_output=True)
    def monthly_allocation_get(period: str) -> PeriodAllocationView:
        """Get the current draft and confirmed allocation state for an explicit YYYY-MM period."""
        return _call_domain(service.get, period)

    @server.tool(name="monthly_allocation_save_draft", structured_output=True)
    def monthly_allocation_save_draft(
        period: str,
        income_idr: StrictInt,
        items: list[AllocationItemInput],
    ) -> AllocationView:
        """Create or update a non-authoritative draft from caller-supplied IDR values."""
        return _call_domain(service.save_draft, period, income_idr, items)

    @server.tool(name="monthly_allocation_confirm", structured_output=True)
    def monthly_allocation_confirm(
        allocation_id: str,
        confirmation_reference: str | None = None,
    ) -> AllocationView:
        """Make an existing draft authoritative after external human confirmation."""
        return _call_domain(service.confirm, allocation_id, confirmation_reference)

    @server.tool(name="monthly_allocation_discard_draft", structured_output=True)
    def monthly_allocation_discard_draft(allocation_id: str) -> AllocationView:
        """Discard an existing draft; confirmed allocations cannot be discarded."""
        return _call_domain(service.discard_draft, allocation_id)

    return server


def main() -> None:
    create_server().run(transport="stdio")


if __name__ == "__main__":
    main()
