from src.agents.analytics_tools import (
    get_dataset_summary,
    get_top_records,
)

TOOLS = {
    "get_dataset_summary": get_dataset_summary,
    "get_top_records": get_top_records,
}


def execute_tool(tool_name: str, arguments: dict) -> dict:
    """Execute only explicitly approved read-only tools."""

    if tool_name not in TOOLS:
        return {
            "status": "error",
            "message": "Tool is not permitted",
        }

    if not isinstance(arguments, dict):
        return {
            "status": "error",
            "message": "Arguments must be a dictionary",
        }

    try:
        result = TOOLS[tool_name](**arguments)

        return {
            "status": "success",
            "tool": tool_name,
            "result": result,
        }

    except (ValueError, TypeError, FileNotFoundError, KeyError) as exc:
        return {
            "status": "error",
            "message": str(exc),
        }
