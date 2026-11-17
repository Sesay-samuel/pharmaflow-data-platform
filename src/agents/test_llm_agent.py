import json
from unittest.mock import MagicMock

from src.agents.llm_agent import (
    clean_response,
    extract_mcp_result,
)


def test_clean_response():
    text = "<think>Internal reasoning</think>Final answer"
    assert clean_response(text) == "Final answer"


def test_clean_response_without_reasoning():
    assert clean_response("PharmaFlow is ready") == "PharmaFlow is ready"


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