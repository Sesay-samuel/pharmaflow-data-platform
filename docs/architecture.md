
# PharmaFlow Architecture

## System Overview

```mermaid
flowchart TD
    A[Pharmacy Synthetic Data] --> B[Python ETL]
    B --> C[(PostgreSQL)]
    B --> D[Apache Airflow]
    D --> E[Bronze - Raw Data]
    E --> F[Silver - Validated Data]
    F --> G[Gold - Analytics]
    G --> H[AWS S3 Data Lake]
    G --> I[Streamlit Dashboard]
    H --> J[AWS Lambda and Reporting API]
    J --> K[CloudWatch Monitoring]
    K --> L[Amazon SNS Email Alerts]
```

## Data Layers

### Bronze
Stores raw source snapshots for traceability.

### Silver
Contains cleaned, standardized and validated records.

### Gold
Contains aggregated analytics datasets, including branch
revenue, medicine revenue and supplier spending.

## Orchestration

Apache Airflow runs the `pharmaflow_medallion_pipeline` DAG.

The pipeline generates source data, processes the medallion
layers, loads relational data and performs quality checks.

## Cloud Infrastructure

AWS S3 stores data lake outputs.

AWS Lambda supports ingestion and reporting services.

Terraform manages CloudWatch alarms, SNS topics and
monitoring permissions.

## Monitoring

CloudWatch tracks Lambda errors and sends alarm
notifications to Amazon SNS.

SNS delivers notifications to a confirmed email subscriber.
```
