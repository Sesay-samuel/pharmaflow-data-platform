
# PharmaFlow Data Engineering Platform

A portfolio data engineering project simulating retail and
wholesale pharmacy operations.

## Day 1 Features

- Synthetic pharmacy dataset generation
- Python ETL pipeline
- PostgreSQL relational database
- Data cleaning and validation
- Retail and wholesale analytics
- Automated unit tests
- Docker Compose environment

## Technology Stack

- Python 3.12
- pandas
- PostgreSQL 16
- SQLAlchemy
- Docker
- pytest

## Local Setup

1. Create and activate a Python virtual environment.
2. Install dependencies using `pip install -r requirements.txt`.
3. Run `docker compose up -d`.
4. Copy `.env.example` to `.env`.
5. Run `python -m src.generate_data`.
6. Run `python -m src.etl_pipeline`.
7. Run `python -m pytest -v`.

## Roadmap

- Apache Airflow orchestration
- AWS S3 and Lambda ingestion
- Amazon Redshift warehouse
- Streamlit analytics dashboard
- Terraform infrastructure
- Kafka and SQS messaging
- Neo4j knowledge graph
- Cloud monitoring and CI/CD

## Data Privacy

All project data is synthetic and is used for demonstration.
No real patient or pharmacy customer data is included.


## Day 2 — Apache Airflow and Medallion Architecture

The platform implements a three-layer data architecture:

- Bronze: original CSV source snapshots
- Silver: cleaned and validated Parquet datasets
- Gold: aggregated analytics-ready Parquet datasets

### Airflow Orchestration

The `pharmaflow_medallion_pipeline` DAG performs:

1. Generate synthetic pharmacy data
2. Ingest Bronze records
3. Transform and validate Silver records
4. Load Silver records into PostgreSQL
5. Generate Gold analytics
6. Execute data quality and reconciliation checks

### Run Airflow Locally

```powershell
docker compose up -d
docker compose -f compose.airflow.yaml build
docker compose -f compose.airflow.yaml up -d
```

Open http://localhost:8081 and trigger the
`pharmaflow_medallion_pipeline` DAG.

### Run Tests

```powershell
python -m pytest -v
```

### Architecture Notes

This is a local development environment using synthetic data.
Airflow uses standalone mode, and the pipeline currently performs
full-refresh loads.

Future enhancements will include incremental processing,
AWS S3 storage, cloud warehousing, CI/CD and monitoring.
