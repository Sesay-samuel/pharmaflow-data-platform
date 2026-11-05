
import json
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
GOLD_DIR = BASE_DIR / "data" / "gold"


def create_summary():
    df = pd.read_parquet(
        GOLD_DIR / "branch_revenue.parquet"
    )

    total_revenue = round(
        float(df["revenue"].sum()), 2
    )

    total_transactions = int(
        df["transactions"].sum()
    )

    summary = {
        "project": "PharmaFlow",
        "branches": int(len(df)),
        "transactions": total_transactions,
        "total_revenue": total_revenue,
        "currency": "GBP",
    }

    output = GOLD_DIR / "api_summary.json"
    output.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    print(f"Created {output}")
    return summary


if __name__ == "__main__":
    create_summary()
