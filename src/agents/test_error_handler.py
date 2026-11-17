
import asyncio

import httpx

from src.agents.error_handler import (
    PharmaFlowAIError,
    handle_ai_error,
)


def test_timeout_error():
    message = handle_ai_error(asyncio.TimeoutError())
    assert "too long" in message


def test_http_timeout():
    message = handle_ai_error(httpx.ReadTimeout("Timed out"))
    assert "too long" in message


def test_connection_error():
    message = handle_ai_error(
        httpx.ConnectError("Connection refused")
    )
    assert "Ollama" in message


def test_custom_error():
    message = handle_ai_error(
        PharmaFlowAIError("Approved operation unavailable")
    )
    assert message == "Approved operation unavailable"


def test_unknown_error_does_not_leak_details():
    message = handle_ai_error(
        RuntimeError("SECRET_INTERNAL_DETAILS")
    )

    assert "SECRET_INTERNAL_DETAILS" not in message
    assert "unexpected error" in message
