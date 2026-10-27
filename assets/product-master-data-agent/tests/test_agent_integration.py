"""Integration tests for the Product Master Data Agent.

Tests the end-to-end agent flow with mocked LLM and mocked MCP tools.
All tests run offline — no network calls to SAP S/4HANA or AI Core.
"""
import json
import sys
from pathlib import Path
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import StructuredTool
from pydantic import create_model

# Ensure app/ is on sys.path for peer-level imports (same as runtime)
_app_path = str(Path(__file__).parent.parent / "app")
if _app_path not in sys.path:
    sys.path.insert(0, _app_path)


def _make_mock_tool(name: str, response: dict) -> StructuredTool:
    """Create a mock StructuredTool with a canned response."""
    async def _call(**kwargs):
        return json.dumps(response)

    ArgsModel = create_model(f"{name}_args")
    return StructuredTool(
        name=name,
        description=f"Mock: {name}",
        args_schema=ArgsModel,
        coroutine=_call,
        handle_tool_error=True,
    )


MOCK_TOOLS = [
    _make_mock_tool("list_a_product_for_api_product_srv", {
        "d": {"results": [{"Product": "P-100", "ProductType": "FERT", "BaseUnit": "PC"}]}
    }),
    _make_mock_tool("get_a_product_for_api_product_srv", {
        "d": {"Product": "P-100", "ProductType": "FERT", "BaseUnit": "PC"}
    }),
    _make_mock_tool("list_a_productdescription_for_api_product_srv", {
        "d": {"results": [{"Product": "P-100", "Language": "EN", "ProductDescription": "Standard Pump 100"}]}
    }),
    _make_mock_tool("list_a_clfnclassforkeydate_for_api_clfn_product_srv", {
        "d": {"results": [{"Product": "P-100", "ClassType": "001", "Class": "PUMP_CLASS"}]}
    }),
    _make_mock_tool("list_productstoragelocation_for_sap_self", {
        "d": {"results": [{"Product": "P-100", "Plant": "1000", "StorageLocation": "0001"}]}
    }),
    _make_mock_tool("list_a_slspricingprocedure_for_api_slspricingprocedure_srv", {
        "d": {"results": [{"SalesPricingProcedure": "RVAA01"}]}
    }),
]


@pytest.mark.asyncio
async def test_agent_invoke_returns_completed_response():
    """Agent returns a completed response for a product query."""
    from agent import SampleAgent

    agent = SampleAgent()
    mock_result = {
        "messages": [
            HumanMessage(content="What is product P-100?"),
            AIMessage(content="Product P-100 is a Standard Pump 100 with base unit PC."),
        ]
    }

    with patch.object(agent, '_run_agent', new=AsyncMock(return_value=mock_result)):
        response = await agent.invoke(
            query="What is product P-100?",
            context_id="test-ctx-001",
            tools=MOCK_TOOLS,
        )

    assert response.status == "completed"
    assert len(response.message) > 0


@pytest.mark.asyncio
async def test_agent_handles_empty_tools():
    """Agent gracefully handles when no tools are available."""
    from agent import SampleAgent

    agent = SampleAgent()
    mock_result = {
        "messages": [
            HumanMessage(content="What is product P-100?"),
            AIMessage(content="Tools are temporarily unavailable."),
        ]
    }

    with patch.object(agent, '_run_agent', new=AsyncMock(return_value=mock_result)):
        response = await agent.invoke(
            query="What is product P-100?",
            context_id="test-ctx-002",
            tools=[],
        )

    assert response.status == "completed"


@pytest.mark.asyncio
async def test_agent_stream_yields_processing_then_complete():
    """Agent stream yields a processing chunk then a final completed chunk."""
    from agent import SampleAgent

    agent = SampleAgent()
    mock_result = {
        "messages": [
            HumanMessage(content="Is P-100 available at plant 1000?"),
            AIMessage(content="Product P-100 has 50 units available at Plant 1000."),
        ]
    }

    chunks = []
    with patch.object(agent, '_run_agent', new=AsyncMock(return_value=mock_result)):
        async for chunk in agent.stream(
            query="Is P-100 available at plant 1000?",
            context_id="test-ctx-003",
            tools=MOCK_TOOLS,
        ):
            chunks.append(chunk)

    assert len(chunks) >= 2
    # First chunk: processing
    assert chunks[0]["is_task_complete"] is False
    assert chunks[0]["content"] == "Processing..."
    # Last chunk: complete
    last = chunks[-1]
    assert last["is_task_complete"] is True
    assert len(last["content"]) > 0


@pytest.mark.asyncio
async def test_agent_error_handling_returns_error_message():
    """Agent returns error message on unexpected exception."""
    from agent import SampleAgent

    agent = SampleAgent()

    with patch.object(agent, '_run_agent', new=AsyncMock(side_effect=RuntimeError("Unexpected error"))):
        response = await agent.invoke(
            query="What is product P-100?",
            context_id="test-ctx-004",
            tools=MOCK_TOOLS,
        )

    assert response.status == "completed"
    assert response.message is not None


@pytest.mark.asyncio
async def test_end_to_end_product_availability_query():
    """Integration test: full product availability query flow."""
    from agent import SampleAgent

    agent = SampleAgent()
    mock_result = {
        "messages": [
            HumanMessage(content="Is product TG11 available at plant 1000?"),
            AIMessage(content="Product TG11 is available at Plant 1000, Storage Location 0001."),
        ]
    }

    with patch.object(agent, '_run_agent', new=AsyncMock(return_value=mock_result)):
        response = await agent.invoke(
            query="Is product TG11 available at plant 1000?",
            context_id="test-ctx-005",
            tools=MOCK_TOOLS,
        )

    assert response.status == "completed"
    assert "TG11" in response.message or "available" in response.message.lower()


@pytest.mark.asyncio
async def test_system_prompt_contains_readonly_constraint():
    """System prompt enforces read-only behavior."""
    from agent import get_system_prompt

    prompt = get_system_prompt()
    assert "read-only" in prompt.lower() or "never create" in prompt.lower() or "strictly read-only" in prompt.lower()


@pytest.mark.asyncio
async def test_system_prompt_instructs_no_data_fabrication():
    """System prompt forbids data fabrication."""
    from agent import get_system_prompt

    prompt = get_system_prompt()
    assert "never fabricate" in prompt.lower() or "must use tools" in prompt.lower()
