
import pandas as pd
import pytest

from src.etl_pipeline import transform


def test_duplicate_medicines_are_removed():
    df = pd.DataFrame([
        {
            "medicine_id": "MED001",
            "medicine_name": "Paracetamol",
            "category": "Pain Relief",
            "unit_price": 2.50,
        },
        {
            "medicine_id": "MED001",
            "medicine_name": "Paracetamol",
            "category": "Pain Relief",
            "unit_price": 2.50,
        },
    ])

    result = transform(df, "medicines")

    assert len(result) == 1


def test_negative_quantities_are_rejected():
    df = pd.DataFrame([
        {
            "sale_id": "SALE001",
            "sale_date": "2026-01-01",
            "branch_id": "BR001",
            "medicine_id": "MED001",
            "quantity": -5,
            "unit_price": 2.50,
            "total_amount": -12.50,
        },
    ])

    result = transform(df, "retail_sales")

    assert result.empty


def test_total_amount_is_recalculated():
    df = pd.DataFrame([
        {
            "sale_id": "SALE002",
            "sale_date": "2026-01-02",
            "branch_id": "BR001",
            "medicine_id": "MED001",
            "quantity": 3,
            "unit_price": 2.50,
            "total_amount": 999.00,
        },
    ])

    result = transform(df, "retail_sales")

    assert result.iloc[0]["total_amount"] == 7.50


def test_missing_required_column_raises_error():
    df = pd.DataFrame([
        {"medicine_id": "MED001"}
    ])

    with pytest.raises(ValueError):
        transform(df, "medicines")
