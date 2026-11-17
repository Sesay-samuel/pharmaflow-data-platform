
import asyncio
import logging

import httpx
from ollama import ResponseError

logger = logging.getLogger(__name__)


class PharmaFlowAIError(Exception):
    """A safe, user-facing AI service error."""


def handle_ai_error(error: Exception) -> str:
    """Convert known AI failures into safe user messages."""

    if isinstance(error, PharmaFlowAIError):
        return str(error)

    if isinstance(error, (asyncio.TimeoutError, httpx.TimeoutException)):
        logger.warning("PharmaFlow AI request timed out")
        return (
            "The AI request took too long to complete. "
            "Please try again."
        )

    if isinstance(error, httpx.ConnectError):
        logger.warning("Unable to connect to Ollama")
        return (
            "Cannot connect to the local Ollama service. "
            "Please start Ollama and try again."
        )

    if isinstance(error, ResponseError):
        logger.warning("Ollama returned an error")
        return (
            "The local AI model could not complete the request. "
            "Please verify that qwen3:4b is installed."
        )

    logger.error(
        "Unexpected PharmaFlow AI failure",
        exc_info=(
            type(error),
            error,
            error.__traceback__,
        ),
    )

    return (
        "An unexpected error occurred while processing "
        "your request. Please try again."
    )
