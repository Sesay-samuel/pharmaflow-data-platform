
import json
import logging
import time
from datetime import datetime, timezone

ALLOWED_AUDIT_TOOLS = frozenset({
    "get_pharmacy_summary",
    "get_pharmacy_top_records",
})

logger = logging.getLogger("pharmaflow.ai.audit")


def record_tool_execution(
    tool_name: str,
    status: str,
    duration_ms: float,
) -> dict:
    """Record safe metadata about an analytics tool execution."""

    if tool_name not in ALLOWED_AUDIT_TOOLS:
        raise ValueError("Audit tool name is not approved")

    if status not in {"success", "error"}:
        raise ValueError("Invalid audit status")

    if (
        isinstance(duration_ms, bool)
        or not isinstance(duration_ms, (int, float))
        or not 0 <= duration_ms < float("inf")
    ):
        raise ValueError("Invalid execution duration")

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool": tool_name,
        "status": status,
        "duration_ms": round(duration_ms, 2),
    }

    logger.info(json.dumps(event))

    return event
