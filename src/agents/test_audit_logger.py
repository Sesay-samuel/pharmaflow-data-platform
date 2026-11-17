
import json
import logging

import pytest

from src.agents.audit_logger import record_tool_execution


from src.agents import audit_logger


@pytest.fixture(autouse=True)
def isolate_audit_log(tmp_path, monkeypatch):
    """Prevent tests from writing to the operational audit log."""

    test_log_path = tmp_path / "ai_audit.jsonl"

    monkeypatch.setattr(
        audit_logger,
        "AUDIT_LOG_PATH",
        test_log_path,
    )



def test_successful_audit_event(caplog):
    with caplog.at_level(
        logging.INFO,
        logger="pharmaflow.ai.audit",
    ):
        event = record_tool_execution(
            "get_pharmacy_summary",
            "success",
            15.567,
        )

    assert event["tool"] == "get_pharmacy_summary"
    assert event["status"] == "success"
    assert event["duration_ms"] == 15.57
    assert "timestamp" in event

    logged_event = json.loads(caplog.records[-1].message)
    assert logged_event == event


def test_failed_audit_event():
    event = record_tool_execution(
        "get_pharmacy_top_records",
        "error",
        25.0,
    )

    assert event["status"] == "error"


def test_reject_unapproved_tool():
    with pytest.raises(ValueError, match="not approved"):
        record_tool_execution(
            "delete_database",
            "success",
            10.0,
        )


def test_reject_invalid_status():
    with pytest.raises(ValueError, match="Invalid audit status"):
        record_tool_execution(
            "get_pharmacy_summary",
            "deleted",
            10.0,
        )


@pytest.mark.parametrize(
    "duration",
    [-1, True, float("nan"), float("inf")],
)
def test_reject_invalid_duration(duration):
    with pytest.raises(ValueError, match="Invalid execution duration"):
        record_tool_execution(
            "get_pharmacy_summary",
            "success",
            duration,
        )


def test_audit_event_contains_only_approved_fields():
    event = record_tool_execution(
        "get_pharmacy_summary",
        "success",
        12.5,
    )

    assert set(event.keys()) == {
        "timestamp",
        "tool",
        "status",
        "duration_ms",
    }

    serialized = json.dumps(event)

    assert "dataset_name" not in serialized
    assert "question" not in serialized
    assert "result" not in serialized
    assert "password" not in serialized
