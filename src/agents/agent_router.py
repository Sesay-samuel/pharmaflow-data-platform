import re

from src.agents.analytics_tools import (
    get_dataset_summary,
    get_top_records,
)

DATASET_KEYWORDS = {
    "branch_revenue": ("branch", "branches"),
    "medicine_revenue": ("medicine", "medicines"),
    "supplier_spend": ("supplier", "suppliers"),
}

RANKING_KEYWORDS = ("top", "highest", "best", "rank", "leading")


def route_question(question: str) -> dict:
    """Route an analytics question to an approved read-only tool."""

    if not isinstance(question, str) or not question.strip():
        raise ValueError("Question must be a non-empty string")

    text = question.lower()

    matches = [
        dataset
        for dataset, keywords in DATASET_KEYWORDS.items()
        if any(
            re.search(r"\b" + re.escape(keyword) + r"\b", text)
            for keyword in keywords
        )
    ]

    if len(matches) != 1:
        return {
            "status": "unsupported",
            "message": "Specify one dataset: branches, medicines, or suppliers.",
        }

    dataset = matches[0]

    ranking = any(
        re.search(r"\b" + keyword + r"\b", text)
        for keyword in RANKING_KEYWORDS
    )

    if ranking:
        match = re.search(r"\btop\s+(\d+)\b", text)
        limit = int(match.group(1)) if match else 5

        return {
            "status": "success",
            "tool": "get_top_records",
            "dataset": dataset,
            "result": get_top_records(dataset, limit),
        }

    if re.search(r"\b(total|summary|summarize|summarise)\b", text):
        return {
            "status": "success",
            "tool": "get_dataset_summary",
            "dataset": dataset,
            "result": get_dataset_summary(dataset),
        }

    return {
        "status": "unsupported",
        "message": "Ask for a total, summary, or top-ranked records.",
    }
