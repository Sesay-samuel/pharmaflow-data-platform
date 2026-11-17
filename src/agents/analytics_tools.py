from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
GOLD_DIR = BASE_DIR / "data" / "gold"

ALLOWED_DATASETS = {
    "branch_revenue": "revenue",
    "medicine_revenue": "revenue",
    "supplier_spend": "total_cost",
}


def load_gold_dataset(dataset_name: str) -> pd.DataFrame:
    """Load an approved Gold-layer dataset in read-only mode."""

    if dataset_name not in ALLOWED_DATASETS:
        raise ValueError(f"Unsupported dataset: {dataset_name}")

    path = GOLD_DIR / dataset_name / "data.parquet"

    if not path.is_file():
        raise FileNotFoundError(f"Gold dataset not found: {dataset_name}")

    return pd.read_parquet(path)


def get_top_records(dataset_name: str, limit: int = 5) -> list[dict]:
    """Return the highest-value records from an approved dataset."""

    if not isinstance(limit, int) or isinstance(limit, bool):
        raise ValueError("Limit must be an integer")

    if not 1 <= limit <= 20:
        raise ValueError("Limit must be between 1 and 20")

    df = load_gold_dataset(dataset_name)
    metric = ALLOWED_DATASETS[dataset_name]

    if metric not in df.columns:
        raise ValueError(f"Missing metric column: {metric}")

    result = df.sort_values(metric, ascending=False).head(limit)

    return result.to_dict(orient="records")


def get_dataset_summary(dataset_name: str) -> dict:
    """Summarise an approved Gold-layer dataset."""

    df = load_gold_dataset(dataset_name)
    metric = ALLOWED_DATASETS[dataset_name]

    if metric not in df.columns:
        raise ValueError(f"Missing metric column: {metric}")

    return {
        "dataset": dataset_name,
        "records": len(df),
        "metric": metric,
        "total": round(float(df[metric].sum()), 2),
    }
