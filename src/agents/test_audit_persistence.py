
import json
import logging

from src.agents import audit_logger


def test_audit_event_is_persisted(tmp_path, monkeypatch):
    audit_file = tmp_path / "logs" / "ai_audit.jsonl"

    monkeypatch.setattr(
        audit_logger,
        "AUDIT_LOG_PATH",
        audit_file,
    )

    event = audit_logger.record_tool_execution(
        "get_pharmacy_summary",
        "success",
        12.345,
    )

    assert audit_file.exists()

    lines = audit_file.read_text(
        encoding="utf-8"
    ).splitlines()

    assert len(lines) == 1
    assert json.loads(lines[0]) == event


def test_multiple_events_are_appended(tmp_path, monkeypatch):
    audit_file = tmp_path / "ai_audit.jsonl"

    monkeypatch.setattr(
        audit_logger,
        "AUDIT_LOG_PATH",
        audit_file,
    )

    audit_logger.record_tool_execution(
        "get_pharmacy_summary",
        "success",
        10.0,
    )

    audit_logger.record_tool_execution(
        "get_pharmacy_top_records",
        "error",
        20.0,
    )

    lines = audit_file.read_text(
        encoding="utf-8"
    ).splitlines()

    assert len(lines) == 2

    assert json.loads(lines[0])["status"] == "success"
    assert json.loads(lines[1])["status"] == "error"


def test_audit_file_contains_only_safe_fields(
    tmp_path,
    monkeypatch,
):
    audit_file = tmp_path / "ai_audit.jsonl"

    monkeypatch.setattr(
        audit_logger,
        "AUDIT_LOG_PATH",
        audit_file,
    )

    audit_logger.record_tool_execution(
        "get_pharmacy_summary",
        "success",
        5.0,
    )

    event = json.loads(
        audit_file.read_text(
            encoding="utf-8"
        ).strip()
    )

    assert set(event) == {
        "timestamp",
        "tool",
        "status",
        "duration_ms",
    }


def test_audit_write_failure_does_not_break_execution(
    tmp_path,
    monkeypatch,
    caplog,
):
    blocked_path = tmp_path / "blocked"

    blocked_path.write_text(
        "This is a file, not a directory.",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        audit_logger,
        "AUDIT_LOG_PATH",
        blocked_path / "ai_audit.jsonl",
    )

    with caplog.at_level(
        logging.WARNING,
        logger="pharmaflow.ai.audit",
    ):
        event = audit_logger.record_tool_execution(
            "get_pharmacy_summary",
            "success",
            10.0,
        )

    assert event["status"] == "success"

    assert "Unable to persist AI audit event" in caplog.text
