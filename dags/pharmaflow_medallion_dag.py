
from datetime import datetime, timedelta, timezone
import os
import subprocess
import sys

from airflow.sdk import dag, task

from src.cloud.upload_to_s3 import upload_all
from src.medallion_pipeline import (
    create_bronze,
    create_silver,
    create_gold,
    load_silver_to_postgres,
    validate_pipeline,
)
from src.quality_checks import run_quality_checks


@dag(
    dag_id="pharmaflow_medallion_pipeline",
    description="PharmaFlow Bronze Silver Gold pipeline with AWS S3 integration",
    schedule=None,
    start_date=datetime(2026, 11, 1, tzinfo=timezone.utc),
    catchup=False,
    max_active_runs=1,
    default_args={
        "owner": "pharmaflow",
        "retries": 1,
        "retry_delay": timedelta(minutes=1),
    },
    tags=[
        "pharmaflow",
        "data-engineering",
        "medallion",
        "aws",
        "s3",
    ],
)
def pharmaflow_pipeline():

    # Task 1: Generate source data
    @task
    def generate_source_data():
        subprocess.run(
            [sys.executable, "-m", "src.generate_data"],
            cwd="/opt/project",
            check=True,
        )

    # Task 2: Bronze ingestion
    @task
    def bronze_ingestion():
        create_bronze()

    # Task 3: Silver transformation
    @task
    def silver_transformation():
        create_silver()

    # Task 4: Load Silver data into PostgreSQL
    @task
    def load_postgresql():
        database_url = os.environ["DATABASE_URL"]
        load_silver_to_postgres(database_url)

    # Task 5: Gold aggregation
    @task
    def gold_aggregation():
        create_gold()

    # Task 6: Data quality validation
    @task
    def quality_validation():
        run_quality_checks()
        validate_pipeline()

    # Task 7: Upload data to AWS S3
    @task
    def upload_cloud_data():
        bucket = os.environ["PHARMAFLOW_S3_BUCKET"]
        region = os.getenv("AWS_DEFAULT_REGION", "eu-west-2")

        upload_all(
            bucket=bucket,
            region=region,
        )

    # Create task instances
    generated = generate_source_data()
    bronze = bronze_ingestion()
    silver = silver_transformation()
    database = load_postgresql()
    gold = gold_aggregation()
    quality = quality_validation()
    cloud = upload_cloud_data()

    # Final dependency chain
    generated >> bronze >> silver >> database >> gold >> quality >> cloud


# Register DAG with Apache Airflow
pharmaflow_pipeline()
