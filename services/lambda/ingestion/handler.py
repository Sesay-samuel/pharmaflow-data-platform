
import json
import logging
import os
from datetime import datetime, timezone
from urllib.parse import unquote_plus

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    s3 = boto3.client("s3")
    expected_bucket = os.environ["DATA_BUCKET"]
    receipts = []

    for record in event.get("Records", []):
        if record.get("eventSource") != "aws:s3":
            continue

        bucket = record["s3"]["bucket"]["name"]
        key = unquote_plus(record["s3"]["object"]["key"])

        if bucket != expected_bucket:
            raise ValueError("Unexpected S3 bucket")

        if not key.startswith("bronze/"):
            logger.info("Skipping non-Bronze key: %s", key)
            continue

        if not key.endswith(".csv"):
            raise ValueError(f"Unexpected file type: {key}")

        metadata = s3.head_object(
            Bucket=bucket,
            Key=key,
        )

        size = metadata["ContentLength"]

        if size <= 0:
            raise ValueError(f"Empty source file: {key}")

        receipt = {
            "source_bucket": bucket,
            "source_key": key,
            "size_bytes": size,
            "status": "validated",
            "validated_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        # Stable receipt key: repeat events update
        # the same receipt instead of creating duplicates.
        receipt_key = (
            "audit/ingestion/"
            + key.removeprefix("bronze/")
            + ".json"
        )

        s3.put_object(
            Bucket=bucket,
            Key=receipt_key,
            Body=json.dumps(receipt).encode("utf-8"),
            ContentType="application/json",
        )

        receipts.append(receipt)
        logger.info("Validated %s (%s bytes)", key, size)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "validated_objects": len(receipts),
            "receipts": receipts,
        }),
    }
