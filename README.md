# PharmaFlow Data Engineering Platform

**End-to-End Data Engineering | Python | PostgreSQL | Apache Airflow | AWS | Docker | Terraform | CI/CD**

PharmaFlow is an end-to-end data engineering portfolio project that simulates pharmacy retail and wholesale operations.
It demonstrates how operational data can be generated, ingested, validated, transformed, orchestrated, stored, and queried using modern data engineering technologies.
The platform uses synthetic datasets and follows a **Bronze, Silver, and Gold medallion architecture**.

### Live Dashboard

**[Launch the PharmaFlow Analytics Dashboard](https://pharmaflow-analytics-dashboard.streamlit.app/)**

The publicly hosted Streamlit application provides interactive analytics for branch revenue, medicine revenue, and supplier spending using synthetic Gold-layer Parquet datasets.
The dashboard runs on Streamlit Community Cloud and does not require AWS credentials or a local PostgreSQL connection.

## Project Highlights

- Built Python ETL pipelines using pandas and SQLAlchemy.
- Processed 10,000 retail sales and 3,000 wholesale orders.
- Implemented automated data validation and transformation.
- Orchestrated data workflows using Apache Airflow.
- Integrated PostgreSQL and Amazon S3 storage.
- Created three curated Gold-layer analytics datasets.
- Registered Parquet datasets in AWS Glue Data Catalog.
- Successfully queried all three datasets using Amazon Athena.
- Provisioned cloud infrastructure using Terraform.
- Implemented automated tests and GitHub Actions CI.
- Developed a Streamlit analytics dashboard.
- Implemented AWS monitoring and cost-awareness controls.

## Architecture

```text
Synthetic Pharmacy Data
          |
          v
   Python ETL Pipeline
          |
          v
 Data Quality Validation
          |
          v
 Bronze / Silver / Gold
          |
     +----+----+
     |         |
     v         v
 PostgreSQL  Amazon S3
               |
               v
        Gold Parquet Data
               |
               v
       AWS Glue Catalog
               |
               v
          Athena SQL
               |
               v
       Analytics Results

Supporting components:
- Apache Airflow: Workflow orchestration
- AWS Lambda / API Gateway: Cloud integration
- Terraform: Infrastructure as code
- Docker: Containerization
- GitHub Actions: CI automation
- CloudWatch / SNS: Monitoring
- Streamlit: Interactive dashboard
```

This diagram provides a conceptual overview of the platform rather than claiming that every component runs in one continuously deployed environment.
See [Architecture Documentation](docs/architecture.md).

## Technology Stack

| Category | Technologies |
|---|---|
| Programming | Python 3.12, SQL |
| Data Processing | pandas, PyArrow |
| Database | PostgreSQL 16, SQLAlchemy |
| Orchestration | Apache Airflow |
| Cloud Storage | Amazon S3 |
| Cloud Integration | AWS Lambda, API Gateway |
| Data Catalog | AWS Glue |
| Serverless Analytics | Amazon Athena |
| Dashboard | Streamlit |
| Infrastructure | Terraform, Docker |
| Monitoring | Amazon CloudWatch, SNS |
| Testing | pytest |
| CI/CD | GitHub Actions, Git |

## Medallion Data Architecture

PharmaFlow organizes its data into three processing layers.

### Bronze Layer

Stores raw synthetic pharmacy data from source systems.

### Silver Layer

Contains cleaned, validated, and standardized data.
Processing includes duplicate handling, required-field validation, quantity checks, and calculated-value verification.

### Gold Layer

Contains curated datasets for business reporting and analytics.
The three principal Gold datasets are:

| Dataset | Purpose |
|---|---|
| `branch_revenue` | Revenue and transaction analysis by branch |
| `medicine_revenue` | Medicine sales and revenue analysis |
| `supplier_spend` | Wholesale supplier purchasing analysis |

## Dataset

The synthetic dataset includes:

| Dataset | Records |
|---|---:|
| Medicines | 30 |
| Suppliers | 12 |
| Branches | 8 |
| Retail sales | 10,000 |
| Wholesale orders | 3,000 |
All records are synthetic. No real patient or customer information is used.

## AWS Data Lake and Analytics

PharmaFlow integrates Amazon S3, AWS Glue Data Catalog, and Amazon Athena.

### Amazon S3

The data lake uses the following prefixes:

```text
audit/
bronze/
silver/
gold/

```
The project has also produced these Gold outputs:

```text
gold/api_summary.json
gold/branch_revenue.parquet
gold/medicine_revenue.parquet
gold/supplier_spend.parquet

```
For the Glue and Athena integration, curated Parquet objects are stored under dataset-specific prefixes:

```text
gold/branch_revenue/data.parquet
gold/medicine_revenue/data.parquet
gold/supplier_spend/data.parquet

```

### AWS Glue Data Catalog

**Database:** `pharmaflow_analytics`
Three external Parquet tables were successfully registered:
- `branch_revenue`
- `medicine_revenue`
- `supplier_spend`

### Amazon Athena

**Workgroup:** `pharmaflow-analytics`
All three Gold datasets were successfully queried using SQL.
Example:

```sql
SELECT *
FROM pharmaflow_analytics.branch_revenue
LIMIT 5;

```

### Verified Athena Results

| Dataset | Query Status | Data Scanned |
|---|---|---:|
| Branch revenue | SUCCEEDED | 883 bytes |
| Medicine revenue | SUCCEEDED | 1,238 bytes |
| Supplier spend | SUCCEEDED | 1,035 bytes |
| **Total** | **3 successful queries** | **3,156 bytes** |
These figures describe the three recorded validation queries, not the total volume of data processed by the platform.
The integration was validated on **15 November 2026**.
See [AWS Glue and Athena Documentation](docs/aws-glue-athena.md).

## Apache Airflow Orchestration

Apache Airflow orchestrates the PharmaFlow data processing workflow.
**DAG ID:** `pharmaflow_medallion_pipeline`
The DAG coordinates processing activities across the medallion pipeline.
Previously verified results include four successful DAG runs.

## PostgreSQL Integration

PostgreSQL provides relational storage for operational datasets.
Verified records include:
- Retail sales: 10,000
- Wholesale orders: 3,000
PostgreSQL runs locally using Docker.

## Streamlit Analytics Dashboard

The Streamlit dashboard presents pharmacy business analytics, including:
- Branch revenue
- Medicine revenue
- Supplier spending
The dashboard can be run locally using Python or Docker.
**Live dashboard:** [Launch PharmaFlow Analytics](https://pharmaflow-analytics-dashboard.streamlit.app/)

The hosted dashboard uses synthetic Gold-layer Parquet files and does not require visitors to provide AWS credentials or connect to PostgreSQL.

## Infrastructure as Code

Terraform is used to manage AWS infrastructure.

### AWS Glue and Athena

The module is located at:
`infrastructure/terraform-glue-athena/`
It provisions:
- One AWS Glue analytics database
- Three external Glue tables
- One Amazon Athena workgroup
All five resources were successfully deployed and verified.

### EC2 and RDS

Terraform configuration for EC2 and RDS is maintained separately under:
`infrastructure/terraform-ec2-rds/`
This infrastructure is separate from the completed Glue and Athena validation milestone.

### Monitoring

The project also includes Terraform-managed monitoring components:
- CloudWatch error alarms
- Amazon SNS monitoring topic
- CloudWatch-to-SNS permissions
SNS email delivery was previously verified.

## Local Development

### Prerequisites

- Python 3.12
- Docker Desktop
- Git
- AWS CLI for cloud operations
- Terraform for infrastructure operations

### Clone Repository

```powershell
git clone https://github.com/Sesay-samuel/pharmaflow-data-platform.git
cd pharmaflow-data-platform

```

### Create Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

```

### Install Dependencies

```powershell
pip install -r requirements.txt

```

### Configure Environment

```powershell
Copy-Item .env.example .env

```
Update `.env` with your local configuration.
Never commit passwords, credentials, or access tokens.

### Start PostgreSQL

```powershell
docker compose up -d

```

### Run ETL Pipeline

```powershell
python -m src.generate_data
python -m src.etl_pipeline

```

### Start Apache Airflow

```powershell
docker compose -f compose.airflow.yaml build
docker compose -f compose.airflow.yaml up -d

```
Open:
`http://localhost:8081`
Trigger the DAG:
`pharmaflow_medallion_pipeline`

### Run Automated Tests

```powershell
python -m pytest -q

```
Previously verified result:
**14 tests passed — 7 November 2026.**

## Testing and Validation

| Component | Verified Result |
|---|---|
| Automated tests | 14 passed |
| PostgreSQL retail sales | 10,000 records |
| PostgreSQL wholesale orders | 3,000 records |
| Airflow DAG runs | 4 successful |
| AWS S3 Gold outputs | 4 files verified |
| AWS Glue tables | 3 verified |
| Athena SQL queries | 3 successful |
| Terraform Glue/Athena resources | 5 deployed |
| Streamlit Docker container | Healthy |
| SNS email delivery | Verified |
| S3 encryption | AES256 |
| S3 versioning | Enabled |
| S3 public-access blocking | Enabled |
See [Testing Documentation](docs/testing.md).

## CI/CD

GitHub Actions provides automated validation of the project.
The AWS Glue and Athena pull request passed four checks:
- Python Tests (push)
- Python Tests (pull request)
- Docker Build (push)
- Docker Build (pull request)
The milestone was merged into `main` through pull request #8.

## Security and Cost Controls

The project uses:
- AWS IAM Identity Center authentication
- Scoped IAM permissions
- S3 encryption and public-access blocking
- SSE-S3 encryption for Athena query results
- A 10 MiB Athena per-query scan cutoff
- AWS Budget alerts with a $5 monthly threshold
- Git exclusions for Terraform state and credentials
AWS Budget alerts are notifications, not hard spending limits.
Cloud resources may incur charges even when usage is small.

## Future Enhancements

- Incremental and change-data-capture pipelines
- Amazon Redshift analytics warehouse
- Kafka or Amazon SQS event processing
- Neo4j knowledge graph integration
- Additional data-quality observability
- Production-grade secrets management
- Dashboard usability improvements and additional analytics

## Documentation

- [Architecture](docs/architecture.md)
- [AWS Glue and Athena Integration](docs/aws-glue-athena.md)
- [Testing](docs/testing.md)

## Data Privacy

All datasets are synthetic.
No real patient, customer, or pharmacy transaction data is used.

## Author

**Samuel Sesay**
[GitHub Repository](https://github.com/Sesay-samuel/pharmaflow-data-platform)
