

import asyncio
import json
import re
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from ollama import AsyncClient

MODEL = "qwen3:4b"

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

    if "</think>" in text:
        text = text.rsplit("</think>", 1)[-1]

    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return text.strip()


def extract_mcp_result(response):
    if response.structuredContent is not None:
        return response.structuredContent

    for item in response.content:
        if item.type == "text":
            return json.loads(item.text)

    raise ValueError("MCP response contains no readable result")


async def ask_pharmaflow(question: str) -> str:
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Question must be a non-empty string")

    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "src.agents.mcp_server"],
    )

    client = AsyncClient(
    host="http://localhost:11434",
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
                if tool.name in {
                    "get_pharmacy_summary",
                    "get_pharmacy_top_records",
                }
            ]

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question},
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
                return clean_response(response.message.content or "") or (
                    "I cannot answer that request with the available tools."
                )

            messages.append(response.message.model_dump(
                exclude_none=True
            ))

            for call in calls[:3]:
                name = call.function.name

                if name not in {
                    "get_pharmacy_summary",
                    "get_pharmacy_top_records",
                }:
                    raise ValueError("Model selected an unapproved tool")

                arguments = call.function.arguments

                if isinstance(arguments, str):
                    arguments = json.loads(arguments)

                result = await session.call_tool(name, arguments)
                data = extract_mcp_result(result)

                if result.isError or data.get("status") != "success":
                    return (
                        "The requested analytics operation could not "
                        f"be completed: {data.get('message', 'Unknown error')}"
                    )

                messages.append({
                    "role": "tool",
                    "tool_name": name,
                    "content": json.dumps(data),
                })

            final_response = await client.chat(
                model=MODEL,
                messages=messages,
                think=False,
                options={"temperature": 0},
            )

            return clean_response(final_response.message.content or "") or (
                "The analytics tool returned data, but the model "
                "did not produce a final answer."
            )


if __name__ == "__main__":
    question = (
        " ".join(sys.argv[1:])
        or "Which are the top 3 pharmacy branches by revenue?"
    )

    print(asyncio.run(ask_pharmaflow(question)))
if __name__ == "__main__":
    question = (
        " ".join(sys.argv[1:])
        or "Which are the top 3 pharmacy branches by revenue?"
    )

    print(asyncio.run(ask_pharmaflow(question)))
