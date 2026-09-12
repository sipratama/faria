from __future__ import annotations

import asyncio

import pytest
from mcp import Client

from faria_household_mcp.server import TOOL_NAMES, create_server


def test_server_exposes_exactly_twelve_constrained_household_tools(tmp_path) -> None:
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

    asyncio.run(scenario())


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
