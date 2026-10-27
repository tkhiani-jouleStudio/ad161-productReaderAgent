"""Unit tests for product master data agent MCP tool interactions.

Tests mock the MCP tools and run offline — no network calls.
"""
import json
import pytest
from langchain_core.tools import StructuredTool
from pydantic import create_model


def _make_tool(name: str, response: dict) -> StructuredTool:
    """Build a StructuredTool that returns a canned JSON response."""
    async def _call(**kwargs):
        return json.dumps(response)

    ArgsModel = create_model(f"{name}_args")
    return StructuredTool(
        name=name,
        description=f"Mock tool: {name}",
        args_schema=ArgsModel,
        coroutine=_call,
        handle_tool_error=True,
    )


@pytest.mark.asyncio
async def test_product_tool_returns_json():
    """Tool returns valid JSON with product data."""
    mock_response = {
        "d": {
            "results": [
                {"Product": "P-100", "ProductDescription": "Standard Pump 100"}
            ]
        }
    }
    tool = _make_tool("list_a_product_for_api_product_srv", mock_response)
    result = await tool.arun({})
    data = json.loads(result)
    assert "d" in data
    assert data["d"]["results"][0]["Product"] == "P-100"


@pytest.mark.asyncio
async def test_product_description_tool():
    """Tool returns product description."""
    mock_response = {
        "d": {
            "results": [
                {"Product": "P-100", "Language": "EN", "ProductDescription": "Standard Pump 100"}
            ]
        }
    }
    tool = _make_tool("list_a_productdescription_for_api_product_srv", mock_response)
    result = await tool.arun({})
    data = json.loads(result)
    assert data["d"]["results"][0]["ProductDescription"] == "Standard Pump 100"


@pytest.mark.asyncio
async def test_get_single_product():
    """Tool returns single product by key."""
    mock_response = {
        "d": {"Product": "P-100", "BaseUnit": "PC", "ProductType": "FERT"}
    }
    tool = _make_tool("get_a_product_for_api_product_srv", mock_response)
    result = await tool.arun({"Product": "P-100"})
    data = json.loads(result)
    assert data["d"]["Product"] == "P-100"


@pytest.mark.asyncio
async def test_classification_tool_returns_class_data():
    """Tool returns product classification data."""
    mock_response = {
        "d": {
            "results": [
                {"Product": "P-100", "ClassType": "001", "Class": "PUMP_CLASS"}
            ]
        }
    }
    tool = _make_tool("list_a_clfnclassforkeydate_for_api_clfn_product_srv", mock_response)
    result = await tool.arun({})
    data = json.loads(result)
    assert data["d"]["results"][0]["ClassType"] == "001"


@pytest.mark.asyncio
async def test_clfn_product_tool():
    """Tool returns classification-enabled product data."""
    mock_response = {
        "d": {"Product": "P-100", "ClassType": "001"}
    }
    tool = _make_tool("get_a_clfnproduct_for_api_clfn_product_srv", mock_response)
    result = await tool.arun({"Product": "P-100"})
    data = json.loads(result)
    assert data["d"]["Product"] == "P-100"


@pytest.mark.asyncio
async def test_storage_location_availability_tool():
    """Tool returns availability per storage location."""
    mock_response = {
        "d": {
            "results": [
                {"Product": "P-100", "Plant": "1000", "StorageLocation": "0001"}
            ]
        }
    }
    tool = _make_tool("list_productstoragelocation_for_sap_self", mock_response)
    result = await tool.arun({})
    data = json.loads(result)
    assert data["d"]["results"][0]["Plant"] == "1000"


@pytest.mark.asyncio
async def test_mrp_area_availability_tool():
    """Tool returns MRP area availability data."""
    mock_response = {
        "d": {
            "results": [
                {"Product": "P-100", "Plant": "1000", "MRPArea": "1000", "MRPType": "PD"}
            ]
        }
    }
    tool = _make_tool("list_productmrparea_for_sap_self", mock_response)
    result = await tool.arun({})
    data = json.loads(result)
    assert data["d"]["results"][0]["MRPType"] == "PD"


@pytest.mark.asyncio
async def test_pricing_procedure_list_tool():
    """Tool returns list of pricing procedures."""
    mock_response = {
        "d": {
            "results": [
                {"SalesPricingProcedure": "RVAA01", "SalesPricingProcedureCategory": "A"}
            ]
        }
    }
    tool = _make_tool("list_a_slspricingprocedure_for_api_slspricingprocedure_srv", mock_response)
    result = await tool.arun({})
    data = json.loads(result)
    assert data["d"]["results"][0]["SalesPricingProcedure"] == "RVAA01"


@pytest.mark.asyncio
async def test_pricing_procedure_item_tool():
    """Tool returns pricing procedure step/item data."""
    mock_response = {
        "d": {
            "results": [
                {"SalesPricingProcedure": "RVAA01", "SalesPricingProcedureStep": "10", "SalesPricingCondType": "PR00"}
            ]
        }
    }
    tool = _make_tool("list_a_slspricingprocedureitem_for_api_slspricingprocedure_srv", mock_response)
    result = await tool.arun({})
    data = json.loads(result)
    assert data["d"]["results"][0]["SalesPricingCondType"] == "PR00"


@pytest.mark.asyncio
async def test_empty_results_list():
    """Tool returns empty results list gracefully."""
    mock_response = {"d": {"results": []}}
    tool = _make_tool("list_a_product_for_api_product_srv", mock_response)
    result = await tool.arun({})
    data = json.loads(result)
    assert data["d"]["results"] == []


@pytest.mark.asyncio
async def test_empty_results_graceful():
    """Tool with empty description results doesn't crash."""
    mock_response = {"d": {"results": []}}
    tool = _make_tool("list_a_productdescription_for_api_product_srv", mock_response)
    result = await tool.arun({})
    data = json.loads(result)
    assert len(data["d"]["results"]) == 0
