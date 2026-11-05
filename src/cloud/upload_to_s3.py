
import argparse
import logging
import os
from pathlib import Path

import boto3

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"

DATASETS = {
    "bronze": [
        "medicines.csv",
        "suppliers.csv",
        "branches.csv",
        "retail_sales.csv",
        "wholesale_orders.csv",
    ],
    "silver": [
        "medicines.parquet",
        "suppliers.parquet",
        "branches.parquet",
        "retail_sales.parquet",
        "wholesale_orders.parquet",
    ],
    "gold": [
        "branch_revenue.parquet",
        "medicine_revenue.parquet",
        "supplier_spend.parquet",
    ],
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)


def upload_layer(s3_client, bucket, layer):
    if layer not in DATASETS:
        raise ValueError(f"Unknown layer: {layer}")

    uploaded = []

    for filename in DATASETS[layer]:
        local_path = DATA_DIR / layer / filename

        if not local_path.is_file():
            raise FileNotFoundError(local_path)

        key = f"{layer}/{filename}"

        s3_client.upload_file(
            str(local_path),
            bucket,
            key,
        )

        uploaded.append(key)
        logger.info("Uploaded s3://%s/%s", bucket, key)

    return uploaded


def upload_all(bucket, region):
    s3_client = boto3.client(
        "s3",
        region_name=region,
    )

    results = {}

    for layer in DATASETS:
        results[layer] = upload_layer(
            s3_client,
            bucket,
            layer,
        )

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bucket",
        default=os.getenv("PHARMAFLOW_S3_BUCKET"),
        required=False,
    )
    parser.add_argument(
        "--region",
        default=os.getenv("AWS_DEFAULT_REGION", "eu-west-2"),
    )
    args = parser.parse_args()

    if not args.bucket:
        parser.error(
            "Provide --bucket or PHARMAFLOW_S3_BUCKET"
        )

    results = upload_all(
        bucket=args.bucket,
        region=args.region,
    )

    total = sum(len(files) for files in results.values())
    logger.info("Upload completed: %s objects", total)


if __name__ == "__main__":
    main()
