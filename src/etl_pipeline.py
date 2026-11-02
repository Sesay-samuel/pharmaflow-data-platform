
from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing from .env")

engine = create_engine(DATABASE_URL)
DATA_DIR = Path("data/raw")

SCHEMAS = {
    "medicines": [
        "medicine_id", "medicine_name",
        "category", "unit_price"
    ],
    "suppliers": [
        "supplier_id", "supplier_name", "city"
    ],
    "branches": [
        "branch_id", "branch_name", "city"
    ],
    "retail_sales": [
        "sale_id", "sale_date", "branch_id",
        "medicine_id", "quantity",
        "unit_price", "total_amount"
    ],
    "wholesale_orders": [
        "order_id", "order_date", "supplier_id",
        "medicine_id", "quantity",
        "unit_cost", "total_cost"
    ],
}

PRIMARY_KEYS = {
    "medicines": "medicine_id",
    "suppliers": "supplier_id",
    "branches": "branch_id",
    "retail_sales": "sale_id",
    "wholesale_orders": "order_id",
}


def extract(table):
    path = DATA_DIR / f"{table}.csv"

    if not path.exists():
        raise FileNotFoundError(path)

    return pd.read_csv(path)



def transform(df, table):
    required = SCHEMAS[table]

    missing = set(required) - set(df.columns)

    if missing:
        raise ValueError(
            f"{table}: missing columns {sorted(missing)}"
        )

    df = df[required].copy()

    # Remove duplicates and missing values
    df = df.drop_duplicates(
        subset=[PRIMARY_KEYS[table]]
    )
    df = df.dropna(subset=required)

    # Validate medicine prices
    if table == "medicines":
        df["unit_price"] = pd.to_numeric(
            df["unit_price"], errors="coerce"
        )

        df = df[
            df["unit_price"].notna()
            & (df["unit_price"] >= 0)
        ].copy()

    # Only transaction tables require date processing
    if table in ("retail_sales", "wholesale_orders"):

        price_column = (
            "unit_price"
            if table == "retail_sales"
            else "unit_cost"
        )

        total_column = (
            "total_amount"
            if table == "retail_sales"
            else "total_cost"
        )

        date_column = (
            "sale_date"
            if table == "retail_sales"
            else "order_date"
        )

        df["quantity"] = pd.to_numeric(
            df["quantity"], errors="coerce"
        )

        df[price_column] = pd.to_numeric(
            df[price_column], errors="coerce"
        )

        df = df.dropna(
            subset=["quantity", price_column]
        )

        df = df[
            (df["quantity"] > 0)
            & (df["quantity"] % 1 == 0)
            & (df[price_column] >= 0)
        ].copy()

        df["quantity"] = df["quantity"].astype(int)

        # Recalculate totals
        df[total_column] = (
            df["quantity"] * df[price_column]
        ).round(2)

        # Convert dates only when records exist
        if not df.empty:
            df[date_column] = pd.to_datetime(
                df[date_column],
                format="%Y-%m-%d",
                errors="raise"
            ).dt.date

    return df

    required = SCHEMAS[table]

    missing = set(required) - set(df.columns)

    if missing:
        raise ValueError(
            f"{table}: missing columns {sorted(missing)}"
        )

    df = df[required].copy()
    df = df.drop_duplicates(
        subset=[PRIMARY_KEYS[table]]
    )
    df = df.dropna(subset=required)

    if table == "medicines":
        df = df[df["unit_price"] >= 0]

    if table in ("retail_sales", "wholesale_orders"):
        df["quantity"] = pd.to_numeric(
            df["quantity"], errors="coerce"
        )

        price_column = (
            "unit_price"
            if table == "retail_sales"
            else "unit_cost"
        )

        total_column = (
            "total_amount"
            if table == "retail_sales"
            else "total_cost"
        )

        df[price_column] = pd.to_numeric(
            df[price_column], errors="coerce"
        )

        df = df.dropna(
            subset=["quantity", price_column]
        )

        df = df[
            (df["quantity"] > 0)
            & (df["quantity"] % 1 == 0)
            & (df[price_column] >= 0)
        ].copy()

        df["quantity"] = df["quantity"].astype(int)

        df[total_column] = (
            df["quantity"] * df[price_column]
        ).round(2)

        
    date_column = (
        "sale_date"
        if table == "retail_sales"
        else "order_date"
)

    if not df.empty:
        df[date_column] = pd.to_datetime(
        df[date_column],
        errors="raise",
        format="%Y-%m-%d"
    ).dt.date


    return df


def run_pipeline():
    print("Starting PharmaFlow ETL...")

    tables = [
        "medicines",
        "suppliers",
        "branches",
        "retail_sales",
        "wholesale_orders",
    ]

    cleaned = {}

    for table in tables:
        raw = extract(table)
        result = transform(raw, table)
        cleaned[table] = result

        print(
            f"{table}: {len(raw):,} extracted, "
            f"{len(result):,} validated"
        )

    medicine_ids = set(
        cleaned["medicines"]["medicine_id"]
    )
    branch_ids = set(
        cleaned["branches"]["branch_id"]
    )
    supplier_ids = set(
        cleaned["suppliers"]["supplier_id"]
    )

    retail = cleaned["retail_sales"]
    wholesale = cleaned["wholesale_orders"]

    if not retail["medicine_id"].isin(medicine_ids).all():
        raise ValueError("Unknown medicine in retail sales")

    if not retail["branch_id"].isin(branch_ids).all():
        raise ValueError("Unknown branch in retail sales")

    if not wholesale["medicine_id"].isin(medicine_ids).all():
        raise ValueError("Unknown medicine in wholesale orders")

    if not wholesale["supplier_id"].isin(supplier_ids).all():
        raise ValueError("Unknown supplier in wholesale orders")

    # All database changes use one transaction.
    with engine.begin() as connection:
        connection.execute(text(
            "TRUNCATE TABLE retail_sales, wholesale_orders, "
            "medicines, suppliers, branches"
        ))

        for table in tables:
            cleaned[table].to_sql(
                table,
                connection,
                if_exists="append",
                index=False,
                chunksize=1000,
                method="multi",
            )

            print(
                f"Loaded {len(cleaned[table]):,} "
                f"rows into {table}"
            )

    print("PharmaFlow ETL completed successfully.")


if __name__ == "__main__":
    run_pipeline()
