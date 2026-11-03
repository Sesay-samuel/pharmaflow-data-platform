
import pandas as pd
import pytest

from src.etl_pipeline import transform
from src.quality_checks import (
    check_unique_ids,
    check_positive_quantities,
)


def test_wholesale_negative_quantity_removed():
    df = pd.DataFrame([
        {
            "order_id": "ORD001",
            "order_date": "2026-01-01",
            "supplier_id": "SUP001",
            "medicine_id": "MED001",
            "quantity": -10,
            "unit_cost": 2.00,
            "total_cost": -20.00,
        }
    ])

    result = transform(df, "wholesale_orders")
    assert result.empty


def test_wholesale_cost_recalculated():
    df = pd.DataFrame([
        {
            "order_id": "ORD002",
            "order_date": "2026-01-01",
            "supplier_id": "SUP001",
            "medicine_id": "MED001",
            "quantity": 20,
            "unit_cost": 2.50,
            "total_cost": 999.00,
        }
    ])

    result = transform(df, "wholesale_orders")
    assert result.iloc[0]["total_cost"] == 50.00


def test_duplicate_id_check_detects_duplicates(
    tmp_path, monkeypatch
):
    import src.quality_checks as quality

    monkeypatch.setattr(
        quality, "SILVER_DIR", tmp_path
    )

    df = pd.DataFrame({
        "medicine_id": ["MED001", "MED001"],
    })

    df.to_parquet(
        tmp_path / "medicines.parquet",
        index=False,
    )

    with pytest.raises(ValueError):
        check_unique_ids("medicines", "medicine_id")


def test_quantity_check_rejects_zero(
    tmp_path, monkeypatch
):
    import src.quality_checks as quality

    monkeypatch.setattr(
        quality, "SILVER_DIR", tmp_path
    )

    df = pd.DataFrame({
        "quantity": [10, 0, 5],
    })

    df.to_parquet(
        tmp_path / "retail_sales.parquet",
        index=False,
    )

    with pytest.raises(ValueError):
        check_positive_quantities("retail_sales")


def test_valid_unique_ids(tmp_path, monkeypatch):
    import src.quality_checks as quality

    monkeypatch.setattr(
        quality, "SILVER_DIR", tmp_path
    )

    df = pd.DataFrame({
        "medicine_id": ["MED001", "MED002"],
    })

    df.to_parquet(
        tmp_path / "medicines.parquet",
        index=False,
    )

    assert check_unique_ids(
        "medicines", "medicine_id"
    ) is True
