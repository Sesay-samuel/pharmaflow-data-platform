
import importlib.util
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[2]


def load_handler(relative_path, module_name):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(
        module_name, path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_api_health():
    api = load_handler(
        "services/lambda/api/handler.py",
        "pharmaflow_api_handler",
    )

    event = {
        "rawPath": "/health",
        "requestContext": {
            "http": {"method": "GET"}
        },
    }

    result = api.lambda_handler(event, None)

    assert result["statusCode"] == 200
    assert json.loads(result["body"])["status"] == "healthy"


def test_api_unknown_route():
    api = load_handler(
        "services/lambda/api/handler.py",
        "pharmaflow_api_unknown",
    )

    event = {
        "rawPath": "/missing",
        "requestContext": {
            "http": {"method": "GET"}
        },
    }

    result = api.lambda_handler(event, None)
    assert result["statusCode"] == 404


def test_api_rejects_post():
    api = load_handler(
        "services/lambda/api/handler.py",
        "pharmaflow_api_post",
    )

    event = {
        "rawPath": "/health",
        "requestContext": {
            "http": {"method": "POST"}
        },
    }

    result = api.lambda_handler(event, None)
    assert result["statusCode"] == 405


def test_ingestion_rejects_wrong_bucket(monkeypatch):
    ingestion = load_handler(
        "services/lambda/ingestion/handler.py",
        "pharmaflow_ingestion_handler",
    )

    monkeypatch.setenv(
        "DATA_BUCKET", "expected-pharmaflow-bucket"
    )

    event = {
        "Records": [{
            "eventSource": "aws:s3",
            "s3": {
                "bucket": {"name": "unexpected-bucket"},
                "object": {"key": "bronze/medicines.csv"},
            },
        }]
    }

    with patch.object(ingestion.boto3, "client"):
        with pytest.raises(ValueError, match="Unexpected"):
            ingestion.lambda_handler(event, None)


def test_ingestion_writes_receipt(monkeypatch):
    ingestion = load_handler(
        "services/lambda/ingestion/handler.py",
        "pharmaflow_ingestion_success",
    )

    monkeypatch.setenv(
        "DATA_BUCKET", "pharmaflow-test-bucket"
    )

    mock_s3 = MagicMock()
    mock_s3.head_object.return_value = {
        "ContentLength": 1024
    }

    event = {
        "Records": [{
            "eventSource": "aws:s3",
            "s3": {
                "bucket": {
                    "name": "pharmaflow-test-bucket"
                },
                "object": {
                    "key": "bronze/medicines.csv"
                },
            },
        }]
    }

    with patch.object(
        ingestion.boto3,
        "client",
        return_value=mock_s3,
    ):
        result = ingestion.lambda_handler(event, None)

    assert result["statusCode"] == 200
    mock_s3.put_object.assert_called_once()

    args = mock_s3.put_object.call_args.kwargs
    assert args["Key"] == (
        "audit/ingestion/medicines.csv.json"
    )
