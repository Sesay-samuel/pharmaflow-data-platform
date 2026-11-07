# PharmaFlow Data Engineering Platform

**End-to-End Data Engineering | Python | PostgreSQL | Apache Airflow | AWS | Docker | Terraform | CI/CD**

PharmaFlow is a portfolio data engineering platform that simulates pharmacy retail and wholesale operations. It demonstrates data ingestion, transformation, validation, orchestration, cloud storage, analytics, monitoring and infrastructure automation.

The project uses synthetic data and follows a Bronze, Silver and Gold medallion architecture.

## Key Features

- Synthetic pharmacy data generation
- Python ETL pipelines with pandas and SQLAlchemy
- PostgreSQL relational data storage
- Apache Airflow pipeline orchestration
- Bronze, Silver and Gold data processing
- Data-quality checks and automated testing
- AWS S3 data lake storage
- AWS Lambda ingestion and reporting components
- Streamlit analytics dashboard
- Docker containerization
- GitHub Actions CI workflow
- Terraform-managed CloudWatch alarms and SNS monitoring

## Technology Stack

| Category | Technologies |
|---|---|
| Programming | Python 3.12, SQL |
| Data Processing | pandas, PyArrow |
| Database | PostgreSQL 16, SQLAlchemy |
| Orchestration | Apache Airflow |
| Cloud | AWS S3, Lambda, API Gateway |
| Analytics | Streamlit |
| Infrastructure | Terraform, Docker |
| Monitoring | Amazon CloudWatch, SNS |
| Testing | pytest |
| CI/CD | GitHub Actions, Git |

## Data Architecture

PharmaFlow follows a medallion data architecture:

**Bronze Layer:** Raw synthetic pharmacy source data.

**Silver Layer:** Cleaned, validated and standardized datasets.

**Gold Layer:** Aggregated datasets for reporting and analytics.

The Gold layer includes:

- Branch revenue
- Medicine revenue
- Supplier spending

See [Architecture Documentation](docs/architecture.md).

## Dataset

The synthetic dataset includes:

| Dataset | Records |
|---|---:|
| Medicines | 30 |
| Suppliers | 12 |
| Branches | 8 |
| Retail sales | 10,000 |
| Wholesale orders | 3,000 |

## Local Development

### Prerequisites

- Python 3.12
- Docker Desktop
- Git
- PostgreSQL through Docker
- AWS CLI for optional cloud operations
- Terraform for monitoring infrastructure

### Installation

Clone the repository:

```powershell
git clone https://github.com/Sesay-samuel/pharmaflow-data-platform.git
cd pharmaflow-data-platform
```

Create a Python virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Configure environment variables:

```powershell
Copy-Item .env.example .env
```

Update `.env` with your local configuration. Never commit credentials.

### Start PostgreSQL

```powershell
docker compose up -d
```

### Run the ETL Pipeline

```powershell
python -m src.generate_data
python -m src.etl_pipeline
```

### Start Apache Airflow

```powershell
docker compose -f compose.airflow.yaml build
docker compose -f compose.airflow.yaml up -d
```

Open http://localhost:8081.

Trigger the DAG:

`pharmaflow_medallion_pipeline`

### Run Automated Tests

```powershell
python -m pytest -q
```

Latest verified result:

**14 tests passed — 7 November 2026.**

## Cloud Data Lake

The AWS S3 data lake contains the following prefixes:

```text
audit/
bronze/
silver/
gold/
```

Verified Gold outputs:

```text
gold/api_summary.json
gold/branch_revenue.parquet
gold/medicine_revenue.parquet
gold/supplier_spend.parquet
```

Cloud deployment requires AWS credentials and appropriate IAM permissions.

## Analytics Dashboard

The Streamlit dashboard provides analytics for:

- Branch revenue
- Medicine revenue
- Supplier spending

The dashboard can be run locally using its Python application or Docker image.

## Monitoring

Terraform provisions:

- CloudWatch error alarms for the ingestion and reporting Lambda functions
- An SNS monitoring topic
- SNS topic permissions for CloudWatch notifications

SNS email delivery was successfully tested.

An existing AWS monthly cost budget is configured separately in AWS Billing.

## Validation Results

| Component | Result |
|---|---|
| Automated tests | 14 passed |
| PostgreSQL retail sales | 10,000 records |
| PostgreSQL wholesale orders | 3,000 records |
| Airflow DAG runs | 4 successful |
| AWS S3 Gold outputs | 4 files verified |
| Streamlit Docker container | Healthy |
| SNS email delivery | Verified |
| S3 encryption | AES256 |
| S3 versioning | Enabled |
| S3 public-access blocking | Enabled |

See [Testing Documentation](docs/testing.md).

## Future Enhancements

- Incremental and change-data-capture pipelines
- Amazon Redshift analytics warehouse
- Kafka or Amazon SQS event processing
- Neo4j knowledge graph
- Additional data-quality observability
- Production-grade secrets management and deployment

## Data Privacy

All datasets are synthetic. No real patient, customer or pharmacy transaction data is used.

## Author

Samuel Sesay

[GitHub Repository](https://github.com/Sesay-samuel/pharmaflow-data-platform)