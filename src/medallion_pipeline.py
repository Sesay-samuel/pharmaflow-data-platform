
from pathlib import Path
from datetime import datetime, timezone
import shutil

import pandas as pd
from sqlalchemy import create_engine, text

from src.etl_pipeline import (
    transform,
    SCHEMAS,
)

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

RAW_DIR = DATA_DIR / "raw"
BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR = DATA_DIR / "gold"

TABLES = [
    "medicines",
    "suppliers",
    "branches",
    "retail_sales",
    "wholesale_orders",
]


def create_bronze():
    """Preserve original CSV source files."""
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)

    for table in TABLES:
        source = RAW_DIR / f"{table}.csv"
        target = BRONZE_DIR / f"{table}.csv"

        if not source.exists():
            raise FileNotFoundError(source)

        shutil.copy2(source, target)
        print(f"BRONZE: copied {table}")

    print("Bronze layer completed")


def create_silver():
    """Validate raw data and save cleaned Parquet files."""
    SILVER_DIR.mkdir(parents=True, exist_ok=True)

    cleaned = {}

    for table in TABLES:
        source = BRONZE_DIR / f"{table}.csv"
        df = pd.read_csv(source)

        result = transform(df, table)
        cleaned[table] = result

        if result.empty:
            raise ValueError(f"{table} has no valid records")

    medicine_ids = set(cleaned["medicines"]["medicine_id"])
    branch_ids = set(cleaned["branches"]["branch_id"])
    supplier_ids = set(cleaned["suppliers"]["supplier_id"])

    retail = cleaned["retail_sales"]
    wholesale = cleaned["wholesale_orders"]

    if not retail["medicine_id"].isin(medicine_ids).all():
        raise ValueError("Invalid retail medicine reference")

    if not retail["branch_id"].isin(branch_ids).all():
        raise ValueError("Invalid retail branch reference")

    if not wholesale["medicine_id"].isin(medicine_ids).all():
        raise ValueError("Invalid wholesale medicine reference")

    if not wholesale["supplier_id"].isin(supplier_ids).all():
        raise ValueError("Invalid wholesale supplier reference")

    for table, df in cleaned.items():
        df.to_parquet(
            SILVER_DIR / f"{table}.parquet",
            index=False,
        )
        print(f"SILVER: {table} -> {len(df):,} rows")

    print("Silver layer completed")


def load_silver_to_postgres(database_url):
    """Load Silver data into PostgreSQL atomically."""
    engine = create_engine(database_url)

    with engine.begin() as connection:
        connection.execute(text(
            "TRUNCATE TABLE retail_sales, wholesale_orders, "
            "medicines, suppliers, branches"
        ))

        for table in TABLES:
            df = pd.read_parquet(
                SILVER_DIR / f"{table}.parquet"
            )

            df.to_sql(
                table,
                connection,
                if_exists="append",
                index=False,
                chunksize=1000,
                method="multi",
            )

            print(f"POSTGRES: loaded {table}: {len(df):,}")

    engine.dispose()
    print("PostgreSQL load completed")


def create_gold():
    """Produce business-ready analytics from Silver data."""
    GOLD_DIR.mkdir(parents=True, exist_ok=True)

    sales = pd.read_parquet(
        SILVER_DIR / "retail_sales.parquet"
    )
    branches = pd.read_parquet(
        SILVER_DIR / "branches.parquet"
    )
    medicines = pd.read_parquet(
        SILVER_DIR / "medicines.parquet"
    )
    wholesale = pd.read_parquet(
        SILVER_DIR / "wholesale_orders.parquet"
    )
    suppliers = pd.read_parquet(
        SILVER_DIR / "suppliers.parquet"
    )

    branch_sales = sales.merge(
        branches,
        on="branch_id",
        validate="many_to_one",
    )

    branch_revenue = (
        branch_sales.groupby(
            ["branch_id", "branch_name", "city"],
            as_index=False,
        )
        .agg(
            transactions=("sale_id", "count"),
            units_sold=("quantity", "sum"),
            revenue=("total_amount", "sum"),
        )
    )

    branch_revenue["revenue"] = (
        branch_revenue["revenue"].round(2)
    )

    medicine_sales = sales.merge(
        medicines[["medicine_id", "medicine_name"]],
        on="medicine_id",
        validate="many_to_one",
    )

    medicine_revenue = (
        medicine_sales.groupby(
            ["medicine_id", "medicine_name"],
            as_index=False,
        )
        .agg(
            units_sold=("quantity", "sum"),
            revenue=("total_amount", "sum"),
        )
    )

    medicine_revenue["revenue"] = (
        medicine_revenue["revenue"].round(2)
    )

    supplier_orders = wholesale.merge(
        suppliers,
        on="supplier_id",
        validate="many_to_one",
    )

    supplier_spend = (
        supplier_orders.groupby(
            ["supplier_id", "supplier_name"],
            as_index=False,
        )
        .agg(
            orders=("order_id", "count"),
            units_ordered=("quantity", "sum"),
            total_cost=("total_cost", "sum"),
        )
    )

    supplier_spend["total_cost"] = (
        supplier_spend["total_cost"].round(2)
    )

    products = {
        "branch_revenue": branch_revenue,
        "medicine_revenue": medicine_revenue,
        "supplier_spend": supplier_spend,
    }

    for name, df in products.items():
        df.to_parquet(
            GOLD_DIR / f"{name}.parquet",
            index=False,
        )
        print(f"GOLD: created {name}: {len(df)} rows")

    print("Gold layer completed")


def validate_pipeline():
    """Check source counts and financial reconciliation."""
    expected = {
        "medicines": 30,
        "suppliers": 12,
        "branches": 8,
        "retail_sales": 10000,
        "wholesale_orders": 3000,
    }

    for table, expected_count in expected.items():
        df = pd.read_parquet(
            SILVER_DIR / f"{table}.parquet"
        )

        if len(df) != expected_count:
            raise ValueError(
                f"{table}: expected {expected_count}, "
                f"found {len(df)}"
            )

    sales = pd.read_parquet(
        SILVER_DIR / "retail_sales.parquet"
    )
    branch_revenue = pd.read_parquet(
        GOLD_DIR / "branch_revenue.parquet"
    )

    silver_total = round(
        float(sales["total_amount"].sum()), 2
    )
    gold_total = round(
        float(branch_revenue["revenue"].sum()), 2
    )

    if abs(silver_total - gold_total) > 0.01:
        raise ValueError(
            "Revenue reconciliation failed: "
            f"Silver={silver_total}, Gold={gold_total}"
        )

    print(
        f"Quality checks passed. Revenue: £{silver_total:,.2f}"
    )
    return True
