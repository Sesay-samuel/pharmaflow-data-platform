
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

ALLOWED_AUDIT_TOOLS = frozenset({
    "get_pharmacy_summary",
    "get_pharmacy_top_records",
})

logger = logging.getLogger("pharmaflow.ai.audit")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_AUDIT_LOG = PROJECT_ROOT / "logs" / "ai_audit.jsonl"

AUDIT_LOG_PATH = DEFAULT_AUDIT_LOG


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

    serialized_event = json.dumps(event)

    logger.info(serialized_event)

    try:
        AUDIT_LOG_PATH.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with AUDIT_LOG_PATH.open(
            "a",
            encoding="utf-8",
        ) as audit_file:
            audit_file.write(serialized_event + "\n")

    except OSError:
        logger.warning(
            "Unable to persist AI audit event"
        )

    return event
