
from datetime import datetime, timedelta, timezone
import os
import subprocess
import sys

from airflow.sdk import dag, task

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
    description="PharmaFlow Bronze Silver Gold pipeline",
    schedule=None,
    start_date=datetime(
        2026, 11, 1, tzinfo=timezone.utc
    ),
    catchup=False,
    max_active_runs=1,
    default_args={
        "owner": "pharmaflow",
        "retries": 1,
        "retry_delay": timedelta(minutes=1),
    },
    tags=["pharmaflow", "data-engineering", "medallion"],
)
def pharmaflow_pipeline():

    @task
    def generate_source_data():
        subprocess.run(
            [sys.executable, "-m", "src.generate_data"],
            cwd="/opt/project",
            check=True,
        )

    @task
    def bronze_ingestion():
        create_bronze()

    @task
    def silver_transformation():
        create_silver()

    @task
    def load_postgresql():
        database_url = os.environ["DATABASE_URL"]
        load_silver_to_postgres(database_url)

    @task
    def gold_aggregation():
        create_gold()

    @task
    def quality_validation():
        run_quality_checks()
        validate_pipeline()

    generated = generate_source_data()
    bronze = bronze_ingestion()
    silver = silver_transformation()
    database = load_postgresql()
    gold = gold_aggregation()
    quality = quality_validation()

    generated >> bronze >> silver >> database >> gold >> quality


pharmaflow_pipeline()
