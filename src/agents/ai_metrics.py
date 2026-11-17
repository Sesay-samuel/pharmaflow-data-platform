
import json
import math
from pathlib import Path

from src.agents.audit_logger import (
    ALLOWED_AUDIT_TOOLS,
    DEFAULT_AUDIT_LOG,
)


def load_audit_events(log_path=None) -> list[dict]:
    """Load valid audit events from a local JSONL file."""

    path = (
        Path(log_path)
        if log_path is not None
        else DEFAULT_AUDIT_LOG
    )

    if not path.is_file():
        return []

    events = []

    try:
        with path.open("r", encoding="utf-8") as file:
            for line in file:
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if not isinstance(event, dict):
                    continue

                if set(event) != {
                    "timestamp",
                    "tool",
                    "status",
                    "duration_ms",
                }:
                    continue

                if event["tool"] not in ALLOWED_AUDIT_TOOLS:
                    continue

                if event["status"] not in {"success", "error"}:
                    continue

                duration = event["duration_ms"]

                if (
                    type(duration) not in (int, float)
                    or not math.isfinite(duration)
                    or duration < 0
                ):
                    continue

                if not isinstance(event["timestamp"], str):
                    continue

                events.append(event)

    except (OSError, UnicodeError):
        return []

    return events


def calculate_ai_metrics(events: list[dict]) -> dict:
    """Calculate AI tool execution metrics."""

    total = len(events)

    successes = sum(
        event["status"] == "success"
        for event in events
    )

    failures = total - successes

    durations = [
        event["duration_ms"]
        for event in events
    ]

    average_duration = (
        round(sum(durations) / total, 2)
        if total
        else 0.0
    )

    success_rate = (
        round((successes / total) * 100, 2)
        if total
        else 0.0
    )

    tool_metrics = {}

    for tool_name in sorted(ALLOWED_AUDIT_TOOLS):
        tool_events = [
            event
            for event in events
            if event["tool"] == tool_name
        ]

        tool_total = len(tool_events)

        tool_successes = sum(
            event["status"] == "success"
            for event in tool_events
        )

        tool_metrics[tool_name] = {
            "executions": tool_total,
            "successes": tool_successes,
            "failures": tool_total - tool_successes,
        }

    return {
        "total_executions": total,
        "successful_executions": successes,
        "failed_executions": failures,
        "success_rate": success_rate,
        "average_duration_ms": average_duration,
        "tools": tool_metrics,
    }


def get_ai_metrics(log_path=None) -> dict:
    """Load persisted events and return aggregate metrics."""

    events = load_audit_events(log_path)

    return calculate_ai_metrics(events)
