from mcp.server.fastmcp import FastMCP

from src.agents.tool_registry import execute_tool

mcp = FastMCP("PharmaFlow Analytics")


@mcp.tool()
def get_pharmacy_summary(dataset_name: str) -> dict:
    """Return a summary of an approved PharmaFlow Gold dataset.

    Allowed datasets: branch_revenue, medicine_revenue, supplier_spend.
    """
    return execute_tool(
        "get_dataset_summary",
        {"dataset_name": dataset_name},
    )


@mcp.tool()
def get_pharmacy_top_records(
    dataset_name: str,
    limit: int = 5,
) -> dict:
    """Return the top records from an approved PharmaFlow Gold dataset.

    Allowed datasets: branch_revenue, medicine_revenue, supplier_spend.
    Limit: 1 to 20.
    """
    return execute_tool(
        "get_top_records",
        {"dataset_name": dataset_name, "limit": limit},
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
