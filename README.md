
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
