
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
SILVER_DIR = BASE_DIR / "data" / "silver"


def check_unique_ids(table, id_column):
    path = SILVER_DIR / f"{table}.parquet"
    df = pd.read_parquet(path)

    if df[id_column].duplicated().any():
        raise ValueError(
            f"Duplicate {id_column} detected in {table}"
        )

    return True


def check_positive_quantities(table):
    path = SILVER_DIR / f"{table}.parquet"
    df = pd.read_parquet(path)

    if (df["quantity"] <= 0).any():
        raise ValueError(
            f"Invalid quantities detected in {table}"
        )

    return True


def run_quality_checks():
    check_unique_ids("medicines", "medicine_id")
    check_unique_ids("retail_sales", "sale_id")
    check_unique_ids("wholesale_orders", "order_id")

    check_positive_quantities("retail_sales")
    check_positive_quantities("wholesale_orders")

    print("All additional data-quality checks passed")


if __name__ == "__main__":
    run_quality_checks()
