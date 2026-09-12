from __future__ import annotations

import asyncio
import sqlite3

import pytest
from mcp import Client

from faria_household_mcp.database import HouseholdDatabase
from faria_household_mcp.monitoring import MonitoringService
from faria_household_mcp.server import TOOL_NAMES, create_server


def test_server_exposes_exactly_eighteen_constrained_household_tools(tmp_path) -> None:
    async def scenario() -> None:
        async with Client(create_server(tmp_path / "faria.db")) as client:
            result = await client.list_tools()
            tools = {tool.name: tool for tool in result.tools}

            assert set(tools) == TOOL_NAMES
            assert set(tools["monthly_allocation_get"].input_schema["properties"]) == {"period"}
            assert set(tools["monthly_allocation_save_draft"].input_schema["properties"]) == {
                "period",
                "income_idr",
                "items",
            }
            assert set(tools["monthly_allocation_confirm"].input_schema["properties"]) == {
                "allocation_id",
                "confirmation_reference",
            }
            assert set(tools["monthly_allocation_discard_draft"].input_schema["properties"]) == {
                "allocation_id"
            }
            assert set(tools["financial_rules_get"].input_schema["properties"]) == set()
            assert set(tools["zakat_calculate"].input_schema["properties"]) == {"thp_idr"}
            assert set(tools["savings_goal_list"].input_schema["properties"]) == {"status"}
            assert set(tools["savings_goal_create"].input_schema["properties"]) == {
                "name",
                "target_amount_idr",
                "description",
                "target_date",
            }
            assert set(tools["savings_goal_get"].input_schema["properties"]) == {"goal_id"}
            assert set(tools["savings_contribution_record"].input_schema["properties"]) == {
                "goal_id",
                "amount_idr",
                "source_allocation_reference",
                "note",
            }
            assert set(tools["giving_list"].input_schema["properties"]) == {"period", "type"}
            assert set(tools["giving_record"].input_schema["properties"]) == {
                "type",
                "amount_idr",
                "period",
                "monthly_allocation_reference",
                "note",
            }
            assert set(tools["routine_list"].input_schema["properties"]) == {
                "include_inactive"
            }
            assert set(tools["routine_get"].input_schema["properties"]) == {"routine_id"}
            assert set(tools["routine_create"].input_schema["properties"]) == {
                "title",
                "schedule_kind",
                "schedule_expression",
                "timezone",
                "description",
            }
            assert set(tools["routine_scheduler_link"].input_schema["properties"]) == {
                "routine_id",
                "scheduler_job_id",
            }
            assert set(tools["routine_complete"].input_schema["properties"]) == {"routine_id"}
            assert set(tools["routine_cancel"].input_schema["properties"]) == {"routine_id"}

            assert len(tools) == 18

    asyncio.run(scenario())


def test_routine_tools_cover_pending_link_complete_and_monitoring(tmp_path) -> None:
    database_path = tmp_path / "faria.db"

    async def scenario() -> None:
        async with Client(create_server(database_path)) as client:
            created_result = await client.call_tool(
                "routine_create",
                {
                    "title": "Synthetic recurring",
                    "schedule_kind": "RECURRING",
                    "schedule_expression": "0 9 20 * *",
                    "timezone": "Asia/Jakarta",
                },
            )
            assert created_result.is_error is False
            created = created_result.structured_content
            assert created["status"] == "PENDING_SCHEDULE"

            linked_result = await client.call_tool(
                "routine_scheduler_link",
                {
                    "routine_id": created["routine_id"],
                    "scheduler_job_id": "cron-synthetic",
                },
            )
            assert linked_result.is_error is False
            assert linked_result.structured_content["status"] == "ACTIVE"

            completed_result = await client.call_tool(
                "routine_complete", {"routine_id": created["routine_id"]}
            )
            assert completed_result.is_error is False
            assert completed_result.structured_content["status"] == "ACTIVE"

            get_result = await client.call_tool(
                "routine_get", {"routine_id": created["routine_id"]}
            )
            assert get_result.is_error is False
            assert get_result.structured_content["last_completed_at"] is not None

    asyncio.run(scenario())
    activities = MonitoringService(HouseholdDatabase(database_path)).list_recent()
    assert [activity.activity_type for activity in activities[:3]] == [
        "HOUSEHOLD_ROUTINE_COMPLETED",
        "HOUSEHOLD_ROUTINE_SCHEDULER_LINKED",
        "HOUSEHOLD_ROUTINE_CREATED",
    ]


def test_tools_complete_draft_confirm_and_get_flow(tmp_path) -> None:
    async def scenario() -> None:
        async with Client(create_server(tmp_path / "faria.db")) as client:
            draft_result = await client.call_tool(
                "monthly_allocation_save_draft",
                {
                    "period": "2099-01",
                    "income_idr": 1_000_000,
                    "items": [{"category": "buffer", "amount_idr": 100_000}],
                },
            )
            assert draft_result.is_error is False
            draft = draft_result.structured_content
            assert draft["status"] == "DRAFT"
            assert draft["authoritative"] is False
            assert draft["remainder_idr"] == 900_000

            confirmed_result = await client.call_tool(
                "monthly_allocation_confirm",
                {
                    "allocation_id": draft["allocation_id"],
                    "confirmation_reference": "synthetic-test",
                },
            )
            assert confirmed_result.is_error is False
            assert confirmed_result.structured_content["status"] == "CONFIRMED"
            assert confirmed_result.structured_content["authoritative"] is True

            get_result = await client.call_tool(
                "monthly_allocation_get",
                {"period": "2099-01"},
            )
            assert get_result.is_error is False
            assert get_result.structured_content["draft"] is None
            assert get_result.structured_content["confirmed"]["allocation_id"] == draft["allocation_id"]

    asyncio.run(scenario())


def test_successful_mutation_records_activity_but_reads_are_quiet(tmp_path) -> None:
    database_path = tmp_path / "faria.db"

    async def scenario() -> None:
        async with Client(create_server(database_path)) as client:
            await client.call_tool("monthly_allocation_get", {"period": "2099-01"})
            draft_result = await client.call_tool(
                "monthly_allocation_save_draft",
                {"period": "2099-01", "income_idr": 1_000_000, "items": []},
            )
            assert draft_result.is_error is False
            await client.call_tool("monthly_allocation_get", {"period": "2099-01"})

    asyncio.run(scenario())
    activities = MonitoringService(HouseholdDatabase(database_path)).list_recent()

    assert len(activities) == 1
    assert activities[0].activity_type == "MONTHLY_ALLOCATION_DRAFT_SAVED"
    assert activities[0].summary == "Monthly allocation draft saved for 2099-01."


def test_monitoring_failure_does_not_fail_successful_financial_mutation(
    tmp_path, monkeypatch
) -> None:
    database_path = tmp_path / "faria.db"

    def monitoring_failure(*args, **kwargs):
        raise sqlite3.OperationalError("synthetic monitoring failure")

    monkeypatch.setattr(MonitoringService, "mark_working", monitoring_failure)
    monkeypatch.setattr(MonitoringService, "record_success", monitoring_failure)

    async def scenario() -> None:
        async with Client(create_server(database_path)) as client:
            result = await client.call_tool(
                "monthly_allocation_save_draft",
                {"period": "2099-01", "income_idr": 1_000_000, "items": []},
            )
            assert result.is_error is False
            assert result.structured_content["status"] == "DRAFT"

    asyncio.run(scenario())
    assert HouseholdDatabase(database_path).get_period_state("2099-01").draft is not None


def test_server_exposes_no_resources_or_prompts(tmp_path) -> None:
    async def scenario() -> None:
        async with Client(create_server(tmp_path / "faria.db")) as client:
            resources = await client.list_resources()
            prompts = await client.list_prompts()

            assert resources.resources == []
            assert prompts.prompts == []

    asyncio.run(scenario())


@pytest.mark.parametrize(
    ("tool_name", "arguments", "expected_message"),
    [
        (
            "monthly_allocation_get",
            {"period": "2099-13"},
            "period must use YYYY-MM",
        ),
        (
            "monthly_allocation_save_draft",
            {"period": "2099-01", "income_idr": 1.5, "items": []},
            "income_idr",
        ),
        (
            "monthly_allocation_save_draft",
            {
                "period": "2099-01",
                "income_idr": 1_000,
                "items": [{"category": "buffer", "amount_idr": True}],
            },
            "amount_idr",
        ),
        (
            "monthly_allocation_confirm",
            {"allocation_id": "not-a-uuid"},
            "allocation_id must be a UUID string",
        ),
        (
            "monthly_allocation_confirm",
            {"allocation_id": "00000000-0000-4000-8000-000000000000"},
            "was not found",
        ),
    ],
)
def test_invalid_tool_input_returns_safe_mcp_error(
    tmp_path,
    tool_name,
    arguments,
    expected_message,
) -> None:
    async def scenario() -> None:
        async with Client(create_server(tmp_path / "faria.db")) as client:
            result = await client.call_tool(tool_name, arguments)

            assert result.is_error is True
            error_text = "\n".join(item.text for item in result.content if hasattr(item, "text"))
            assert expected_message in error_text
            assert "Traceback" not in error_text
            assert str(tmp_path) not in error_text

    asyncio.run(scenario())
