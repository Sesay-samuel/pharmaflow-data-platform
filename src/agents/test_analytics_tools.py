import pytest

from src.agents.analytics_tools import (
    get_dataset_summary,
    get_top_records,
)


def test_branch_summary():
    result = get_dataset_summary("branch_revenue")

    assert result["dataset"] == "branch_revenue"
    assert result["records"] > 0
    assert result["total"] >= 0


def test_top_branches():
    result = get_top_records("branch_revenue", 3)

    assert len(result) == 3

    revenues = [row["revenue"] for row in result]
    assert revenues == sorted(revenues, reverse=True)


def test_unknown_dataset_rejected():
    with pytest.raises(ValueError):
        get_dataset_summary("private_credentials")


def test_invalid_limit_rejected():
    with pytest.raises(ValueError):
        get_top_records("branch_revenue", 100)


def test_boolean_limit_rejected():
    with pytest.raises(ValueError):
        get_top_records("branch_revenue", True)
