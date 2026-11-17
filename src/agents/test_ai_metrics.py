
import json

from src.agents.ai_metrics import (
    calculate_ai_metrics,
    get_ai_metrics,
    load_audit_events,
)


def make_event(tool, status, duration):
    return {
        "timestamp": "2026-11-17T16:00:00+00:00",
        "tool": tool,
        "status": status,
        "duration_ms": duration,
    }


def test_empty_metrics():
    metrics = calculate_ai_metrics([])

    assert metrics["total_executions"] == 0
    assert metrics["successful_executions"] == 0
    assert metrics["failed_executions"] == 0
    assert metrics["success_rate"] == 0.0
    assert metrics["average_duration_ms"] == 0.0


def test_success_and_failure_metrics():
    events = [
        make_event("get_pharmacy_summary", "success", 10),
        make_event("get_pharmacy_summary", "success", 20),
        make_event("get_pharmacy_top_records", "error", 30),
    ]

    metrics = calculate_ai_metrics(events)

    assert metrics["total_executions"] == 3
    assert metrics["successful_executions"] == 2
    assert metrics["failed_executions"] == 1
    assert metrics["success_rate"] == 66.67
    assert metrics["average_duration_ms"] == 20.0


def test_per_tool_metrics():
    events = [
        make_event("get_pharmacy_summary", "success", 10),
        make_event("get_pharmacy_summary", "error", 20),
        make_event("get_pharmacy_top_records", "success", 30),
    ]

    metrics = calculate_ai_metrics(events)

    summary = metrics["tools"]["get_pharmacy_summary"]
    ranking = metrics["tools"]["get_pharmacy_top_records"]

    assert summary["executions"] == 2
    assert summary["successes"] == 1
    assert summary["failures"] == 1

    assert ranking["executions"] == 1
    assert ranking["successes"] == 1


def test_missing_audit_file(tmp_path):
    events = load_audit_events(
        tmp_path / "missing.jsonl"
    )

    assert events == []


def test_load_valid_events(tmp_path):
    log_file = tmp_path / "audit.jsonl"

    events = [
        make_event("get_pharmacy_summary", "success", 10),
        make_event("get_pharmacy_top_records", "error", 20),
    ]

    log_file.write_text(
        "\n".join(json.dumps(event) for event in events),
        encoding="utf-8",
    )

    assert load_audit_events(log_file) == events


def test_invalid_events_are_ignored(tmp_path):
    log_file = tmp_path / "audit.jsonl"

    valid = make_event(
        "get_pharmacy_summary",
        "success",
        10,
    )

    invalid_tool = make_event(
        "delete_database",
        "success",
        20,
    )

    log_file.write_text(
        "\n".join([
            json.dumps(valid),
            "{invalid json",
            json.dumps(invalid_tool),
            json.dumps({"unexpected": "event"}),
        ]),
        encoding="utf-8",
    )

    events = load_audit_events(log_file)

    assert events == [valid]


def test_get_ai_metrics_from_file(tmp_path):
    log_file = tmp_path / "audit.jsonl"

    event = make_event(
        "get_pharmacy_summary",
        "success",
        15,
    )

    log_file.write_text(
        json.dumps(event) + "\n",
        encoding="utf-8",
    )

    metrics = get_ai_metrics(log_file)

    assert metrics["total_executions"] == 1
    assert metrics["successful_executions"] == 1
    assert metrics["success_rate"] == 100.0
