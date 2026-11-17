from src.agents.tool_registry import execute_tool


def test_execute_approved_tool():
    result = execute_tool(
        "get_dataset_summary",
        {"dataset_name": "branch_revenue"},
    )

    assert result["status"] == "success"
    assert result["result"]["records"] == 8


def test_reject_unknown_tool():
    result = execute_tool("delete_database", {})

    assert result["status"] == "error"


def test_reject_invalid_arguments():
    result = execute_tool(
        "get_dataset_summary",
        {"dataset_name": "unknown_dataset"},
    )

    assert result["status"] == "error"


def test_reject_non_dictionary_arguments():
    result = execute_tool(
        "get_dataset_summary",
        "branch_revenue",
    )

    assert result["status"] == "error"


def test_execute_top_records():
    result = execute_tool(
        "get_top_records",
        {"dataset_name": "medicine_revenue", "limit": 3},
    )

    assert result["status"] == "success"
    assert len(result["result"]) == 3
