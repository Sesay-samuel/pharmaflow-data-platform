
import csv
import io
import json
import os

import boto3


def response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body),
    }


def lambda_handler(event, context):
    path = event.get("rawPath", "/")
    method = event.get(
        "requestContext", {}
    ).get("http", {}).get("method", "GET")

    if method != "GET":
        return response(405, {"error": "Method not allowed"})

    if path == "/health":
        return response(200, {
            "service": "pharmaflow-api",
            "status": "healthy",
        })

    if path == "/summary":
        bucket = os.environ["DATA_BUCKET"]
        s3 = boto3.client("s3")

        # Day 3 API uses a small JSON summary generated
        # from Gold Parquet, avoiding a pandas Lambda layer.
        obj = s3.get_object(
            Bucket=bucket,
            Key="gold/api_summary.json",
        )

        summary = json.loads(
            obj["Body"].read().decode("utf-8")
        )

        return response(200, summary)

    return response(404, {"error": "Not found"})
