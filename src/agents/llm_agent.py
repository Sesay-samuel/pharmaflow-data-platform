
import asyncio
import json
import re
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from ollama import AsyncClient


MODEL = "qwen3:4b"
OLLAMA_HOST = "http://localhost:11434"

ALLOWED_DATASETS = {
    "branch_revenue",
    "medicine_revenue",
    "supplier_spend",
}

ALLOWED_TOOLS = {
    "get_pharmacy_summary",
    "get_pharmacy_top_records",
}


SYSTEM_PROMPT = """
You are PharmaFlow's read-only pharmacy analytics assistant.

Use the available tools to answer questions about:
- Pharmacy branch revenue
- Medicine revenue
- Supplier spending

Allowed datasets:
branch_revenue, medicine_revenue, supplier_spend.

Always use a tool for numerical analytics.
Never invent figures or claim to have modified data.
Do not attempt destructive or administrative operations.
If a request is unsupported, explain the limitation.

Do not show internal reasoning or thinking steps.
Provide only the final answer.
Do not assume a currency unless the dataset specifies it.
Keep answers concise and grounded in tool results.
"""


def clean_response(text: str) -> str:
    """Remove exposed reasoning from the model response."""

    if not isinstance(text, str):
        return ""

    if "</think>" in text:
        text = text.rsplit("</think>", 1)[-1]

    text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL,
    )

    return text.strip()


def extract_mcp_result(response) -> dict:
    """Extract and validate an MCP analytics response."""

    data = response.structuredContent

    if data is None:
        for item in response.content:
            if item.type == "text":
                try:
                    data = json.loads(item.text)
                except (
                    json.JSONDecodeError,
                    TypeError,
                ) as exc:
                    raise ValueError(
                        "MCP returned invalid JSON"
                    ) from exc

                break

    if data is None:
        raise ValueError(
            "MCP response contains no readable result"
        )

    if not isinstance(data, dict):
        raise ValueError(
            "MCP response must contain a JSON object"
        )

    if data.get("status") not in {
        "success",
        "error",
    }:
        raise ValueError(
            "MCP response has an invalid status"
        )

    return data


def validate_tool_arguments(
    tool_name: str,
    arguments,
) -> dict:
    """Validate model-generated tool arguments."""

    if tool_name not in ALLOWED_TOOLS:
        raise ValueError(
            "AI model selected an unapproved tool"
        )

    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "AI model returned invalid tool arguments"
            ) from exc

    if not isinstance(arguments, dict):
        raise ValueError(
            "AI model returned an invalid argument structure"
        )

    dataset_name = arguments.get("dataset_name")

    if (
        not isinstance(dataset_name, str)
        or dataset_name not in ALLOWED_DATASETS
    ):
        raise ValueError(
            "AI model requested an unsupported dataset"
        )

    if tool_name == "get_pharmacy_summary":
        if set(arguments) != {"dataset_name"}:
            raise ValueError(
                "Invalid summary tool arguments"
            )

    elif tool_name == "get_pharmacy_top_records":
        if not set(arguments).issubset(
            {"dataset_name", "limit"}
        ):
            raise ValueError(
                "Invalid ranking tool arguments"
            )

        limit = arguments.get("limit", 5)

        if (
            type(limit) is not int
            or not 1 <= limit <= 20
        ):
            raise ValueError(
                "Ranking limit must be between 1 and 20"
            )

    return arguments


async def ask_pharmaflow(question: str) -> str:
    """Answer pharmacy analytics questions using Ollama and MCP."""

    if (
        not isinstance(question, str)
        or not question.strip()
    ):
        raise ValueError(
            "Question must be a non-empty string"
        )

    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "src.agents.mcp_server"],
    )

    client = AsyncClient(
        host=OLLAMA_HOST,
        timeout=180.0,
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            available = await session.list_tools()

            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": tool.inputSchema,
                    },
                }
                for tool in available.tools
                if tool.name in ALLOWED_TOOLS
            ]

            if not tools:
                raise RuntimeError(
                    "No approved MCP analytics tools are available"
                )

            messages = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": question.strip(),
                },
            ]

            response = await client.chat(
                model=MODEL,
                messages=messages,
                tools=tools,
                think=False,
                options={"temperature": 0},
            )

            calls = response.message.tool_calls or []

            if not calls:
                return (
                    clean_response(
                        response.message.content or ""
                    )
                    or (
                        "I cannot answer that request "
                        "with the available tools."
                    )
                )

            messages.append(
                response.message.model_dump(
                    exclude_none=True
                )
            )

            for call in calls[:3]:
                name = call.function.name

                arguments = validate_tool_arguments(
                    name,
                    call.function.arguments,
                )

                result = await session.call_tool(
                    name,
                    arguments,
                )

                data = extract_mcp_result(result)

                if (
                    result.isError
                    or data.get("status") != "success"
                ):
                    return (
                        "The requested analytics operation "
                        "could not be completed. "
                        "Please check the dataset and "
                        "try again."
                    )

                messages.append(
                    {
                        "role": "tool",
                        "tool_name": name,
                        "content": json.dumps(data),
                    }
                )

            final_response = await client.chat(
                model=MODEL,
                messages=messages,
                think=False,
                options={"temperature": 0},
            )

            return (
                clean_response(
                    final_response.message.content or ""
                )
                or (
                    "The analytics tool returned data, "
                    "but the model did not produce "
                    "a final answer."
                )
            )


if __name__ == "__main__":
    question = (
        " ".join(sys.argv[1:])
        or "Which are the top 3 pharmacy branches by revenue?"
    )

    print(asyncio.run(ask_pharmaflow(question)))
