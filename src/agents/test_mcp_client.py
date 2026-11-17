import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def extract_result(response):
    """Extract a JSON result from an MCP tool response."""

    if response.structuredContent is not None:
        return response.structuredContent

    for item in response.content:
        if item.type == "text":
            try:
                return json.loads(item.text)
            except json.JSONDecodeError:
                return {"message": item.text}

    raise ValueError("MCP response contains no readable result")


async def main():
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "src.agents.mcp_server"],
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("MCP CONNECTION SUCCESSFUL")

            tools = await session.list_tools()
            names = [tool.name for tool in tools.tools]

            print("AVAILABLE TOOLS:", names)

            assert set(names) == {
                "get_pharmacy_summary",
                "get_pharmacy_top_records",
            }

            summary_response = await session.call_tool(
                "get_pharmacy_summary",
                {"dataset_name": "branch_revenue"},
            )
            assert not summary_response.isError

            summary = extract_result(summary_response)
            assert summary["status"] == "success"
            assert summary["result"]["records"] == 8
            assert summary["result"]["total"] == 1264367.38

            print("BRANCH SUMMARY:")
            print(json.dumps(summary, indent=2))

            ranking_response = await session.call_tool(
                "get_pharmacy_top_records",
                {"dataset_name": "branch_revenue", "limit": 3},
            )
            assert not ranking_response.isError

            ranking = extract_result(ranking_response)
            assert ranking["status"] == "success"
            assert len(ranking["result"]) == 3

            print("TOP THREE BRANCHES:")
            print(json.dumps(ranking, indent=2))

            rejected_response = await session.call_tool(
                "get_pharmacy_summary",
                {"dataset_name": "private_credentials"},
            )

            rejected = extract_result(rejected_response)
            assert rejected["status"] == "error"

            print("UNAPPROVED DATASET:")
            print(json.dumps(rejected, indent=2))

            print("ALL MCP INTEGRATION CHECKS PASSED")


if __name__ == "__main__":
    asyncio.run(main())
