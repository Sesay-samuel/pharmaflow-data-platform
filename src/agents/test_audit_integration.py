
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agents.llm_agent import execute_audited_tool


def make_response(status="success", is_error=False):
    response = MagicMock()
    response.structuredContent = {
        "status": status,
        "result": {"total": 100.0},
    }
    response.isError = is_error
    return response


def test_successful_tool_execution_is_audited():
    session = MagicMock()
    session.call_tool = AsyncMock(
        return_value=make_response()
    )

    with patch(
        "src.agents.llm_agent.record_tool_execution"
    ) as audit:
        result = asyncio.run(
            execute_audited_tool(
                session,
                "get_pharmacy_summary",
                {"dataset_name": "branch_revenue"},
            )
        )

    assert result["status"] == "success"
    audit.assert_called_once()

    kwargs = audit.call_args.kwargs
    assert kwargs["tool_name"] == "get_pharmacy_summary"
    assert kwargs["status"] == "success"
    assert kwargs["duration_ms"] >= 0


def test_failed_tool_execution_is_audited():
    session = MagicMock()
    session.call_tool = AsyncMock(
        return_value=make_response(status="error")
    )

    with patch(
        "src.agents.llm_agent.record_tool_execution"
    ) as audit:
        result = asyncio.run(
            execute_audited_tool(
                session,
                "get_pharmacy_summary",
                {"dataset_name": "branch_revenue"},
            )
        )

    assert result["status"] == "error"
    assert audit.call_args.kwargs["status"] == "error"


def test_tool_exception_is_audited():
    session = MagicMock()
    session.call_tool = AsyncMock(
        side_effect=RuntimeError("MCP unavailable")
    )

    with patch(
        "src.agents.llm_agent.record_tool_execution"
    ) as audit:
        with pytest.raises(RuntimeError, match="MCP unavailable"):
            asyncio.run(
                execute_audited_tool(
                    session,
                    "get_pharmacy_summary",
                    {"dataset_name": "branch_revenue"},
                )
            )

    assert audit.call_args.kwargs["status"] == "error"


def test_malformed_mcp_response_is_audited():
    session = MagicMock()

    response = MagicMock()
    response.structuredContent = None
    response.content = []

    session.call_tool = AsyncMock(return_value=response)

    with patch(
        "src.agents.llm_agent.record_tool_execution"
    ) as audit:
        with pytest.raises(ValueError, match="no readable result"):
            asyncio.run(
                execute_audited_tool(
                    session,
                    "get_pharmacy_summary",
                    {"dataset_name": "branch_revenue"},
                )
            )

    assert audit.call_args.kwargs["status"] == "error"


def test_unapproved_tool_never_executes():
    session = MagicMock()
    session.call_tool = AsyncMock()

    with patch(
        "src.agents.llm_agent.record_tool_execution"
    ) as audit:
        with pytest.raises(ValueError, match="unapproved tool"):
            asyncio.run(
                execute_audited_tool(
                    session,
                    "delete_all_records",
                    {"dataset_name": "branch_revenue"},
                )
            )

    session.call_tool.assert_not_awaited()
    audit.assert_not_called()


def test_invalid_dataset_never_executes():
    session = MagicMock()
    session.call_tool = AsyncMock()

    with patch(
        "src.agents.llm_agent.record_tool_execution"
    ) as audit:
        with pytest.raises(ValueError, match="unsupported dataset"):
            asyncio.run(
                execute_audited_tool(
                    session,
                    "get_pharmacy_summary",
                    {"dataset_name": "private_records"},
                )
            )

    session.call_tool.assert_not_awaited()
    audit.assert_not_called()
