
import json
from unittest.mock import MagicMock

import pytest

from src.agents.llm_agent import (
    clean_response,
    extract_mcp_result,
    validate_tool_arguments,
)


# --------------------------------------------------
# Existing response-cleaning tests
# --------------------------------------------------

def test_clean_response():
    text = "<think>Internal reasoning</think>Final answer"
    assert clean_response(text) == "Final answer"


def test_clean_response_without_reasoning():
    assert clean_response("PharmaFlow is ready") == "PharmaFlow is ready"


# --------------------------------------------------
# Existing MCP response tests
# --------------------------------------------------

def test_extract_structured_mcp_result():
    response = MagicMock()
    response.structuredContent = {
        "status": "success",
        "result": {"total": 100.0},
    }

    result = extract_mcp_result(response)

    assert result["status"] == "success"
    assert result["result"]["total"] == 100.0


def test_extract_text_mcp_result():
    response = MagicMock()
    response.structuredContent = None

    item = MagicMock()
    item.type = "text"
    item.text = json.dumps({
        "status": "success",
        "result": {"total": 8089614.84},
    })

    response.content = [item]

    result = extract_mcp_result(response)

    assert result["result"]["total"] == 8089614.84


def test_extract_empty_mcp_result():
    response = MagicMock()
    response.structuredContent = None
    response.content = []

    try:
        extract_mcp_result(response)
    except ValueError as error:
        assert "no readable result" in str(error)
    else:
        raise AssertionError("Expected ValueError")


# --------------------------------------------------
# New security and tool-validation tests
# --------------------------------------------------

def test_approved_summary_tool():
    arguments = {
        "dataset_name": "branch_revenue",
    }

    result = validate_tool_arguments(
        "get_pharmacy_summary",
        arguments,
    )

    assert result == arguments


def test_approved_ranking_tool():
    arguments = {
        "dataset_name": "medicine_revenue",
        "limit": 3,
    }

    result = validate_tool_arguments(
        "get_pharmacy_top_records",
        arguments,
    )

    assert result == arguments


def test_reject_unapproved_tool():
    with pytest.raises(ValueError, match="unapproved tool"):
        validate_tool_arguments(
            "delete_all_records",
            {"dataset_name": "branch_revenue"},
        )


def test_reject_unsupported_dataset():
    with pytest.raises(ValueError, match="unsupported dataset"):
        validate_tool_arguments(
            "get_pharmacy_summary",
            {"dataset_name": "customer_passwords"},
        )


def test_reject_invalid_json_arguments():
    with pytest.raises(ValueError, match="invalid tool arguments"):
        validate_tool_arguments(
            "get_pharmacy_summary",
            "{invalid json}",
        )


def test_reject_non_dictionary_arguments():
    with pytest.raises(ValueError, match="invalid argument structure"):
        validate_tool_arguments(
            "get_pharmacy_summary",
            ["branch_revenue"],
        )


def test_reject_extra_summary_arguments():
    with pytest.raises(ValueError, match="Invalid summary"):
        validate_tool_arguments(
            "get_pharmacy_summary",
            {
                "dataset_name": "branch_revenue",
                "delete": True,
            },
        )


def test_reject_extra_ranking_arguments():
    with pytest.raises(ValueError, match="Invalid ranking"):
        validate_tool_arguments(
            "get_pharmacy_top_records",
            {
                "dataset_name": "branch_revenue",
                "limit": 3,
                "overwrite": True,
            },
        )


def test_reject_ranking_limit_above_maximum():
    with pytest.raises(ValueError, match="between 1 and 20"):
        validate_tool_arguments(
            "get_pharmacy_top_records",
            {
                "dataset_name": "branch_revenue",
                "limit": 1000,
            },
        )


def test_reject_ranking_limit_zero():
    with pytest.raises(ValueError, match="between 1 and 20"):
        validate_tool_arguments(
            "get_pharmacy_top_records",
            {
                "dataset_name": "branch_revenue",
                "limit": 0,
            },
        )


def test_reject_boolean_ranking_limit():
    with pytest.raises(ValueError, match="between 1 and 20"):
        validate_tool_arguments(
            "get_pharmacy_top_records",
            {
                "dataset_name": "branch_revenue",
                "limit": True,
            },
        )


def test_accept_valid_json_arguments():
    arguments = json.dumps({
        "dataset_name": "supplier_spend",
        "limit": 5,
    })

    result = validate_tool_arguments(
        "get_pharmacy_top_records",
        arguments,
    )

    assert result == {
        "dataset_name": "supplier_spend",
        "limit": 5,
    }
