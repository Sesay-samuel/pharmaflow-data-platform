
# PharmaFlow — AWS Glue & Amazon Athena Analytics

## Overview

PharmaFlow is an end-to-end pharmacy retail and wholesale data engineering platform.

This module demonstrates serverless analytics on AWS using Amazon S3, AWS Glue Data Catalog, Amazon Athena, and Terraform.

Three curated Gold-layer datasets are stored in Parquet format on Amazon S3 and registered as external tables in AWS Glue. Amazon Athena queries these datasets directly using SQL.

**Deployment status:** Successfully deployed and validated on 15 November 2026.

## Architecture

```text
Pharmacy Retail & Wholesale Data
                |
                v
       Python ETL Pipeline
                |
                v
     Bronze / Silver / Gold
                |
                v
       Amazon S3 (Gold)
                |
                v
      AWS Glue Data Catalog
                |
                v
          Amazon Athena
                |
                v
       SQL Analytics Results
```

### AWS Services

| Service | Purpose |
|---------|---------|
| Amazon S3 | Stores curated Parquet datasets and Athena query results |
| AWS Glue Data Catalog | Maintains database, table schemas, and S3 locations |
| Amazon Athena | Executes serverless SQL queries against S3 datasets |
| Terraform | Provisions and manages AWS infrastructure |
| IAM Identity Center | Provides controlled AWS access through SSO |

**AWS Region:** `eu-west-2`

## Infrastructure as Code

Terraform configuration is maintained in:

`infrastructure/terraform-glue-athena/`

Terraform provisions five resources:

1. AWS Glue database: `pharmaflow_analytics`
2. AWS Glue table: `branch_revenue`
3. AWS Glue table: `medicine_revenue`
4. AWS Glue table: `supplier_spend`
5. Amazon Athena workgroup: `pharmaflow-analytics`

The deployment was verified using:

```powershell
terraform state list
```

All five resources were confirmed in Terraform state.

### Deployment Commands

From the Terraform module directory:

```powershell
terraform init
terraform validate
terraform plan
```

Review the proposed changes before applying them.

```powershell
terraform apply
```

Do not apply an unreviewed plan to an existing AWS environment.

## AWS Glue Data Catalog

Database:

`pharmaflow_analytics`

The database contains three external Parquet tables.

| Table | S3 Dataset |
|-------|------------|
| branch_revenue | gold/branch_revenue/ |
| medicine_revenue | gold/medicine_revenue/ |
| supplier_spend | gold/supplier_spend/ |

Each table uses the Parquet Hive SerDe and points to its corresponding Amazon S3 prefix.

The tables were verified using the AWS CLI:

```powershell
aws glue get-tables `
  --database-name pharmaflow_analytics `
  --region eu-west-2 `
  --profile pharmaflow-dev
```

## Amazon Athena Configuration

**Workgroup:** `pharmaflow-analytics`

**Status:** ENABLED

**Query results prefix:**

`s3://pharmaflow-data-673502297238-eu-west-2/athena-results/`

**Per-query data scan cutoff:** 10 MiB

The workgroup uses SSE-S3 encryption for query results.

The scan cutoff limits data scanned by an individual query. It is not an overall AWS spending limit.

## SQL Validation

All three Gold datasets were queried successfully using Amazon Athena.

### 1. Branch Revenue

```sql
SELECT *
FROM pharmaflow_analytics.branch_revenue
LIMIT 5;
```

**Result:** SUCCEEDED

**Data scanned:** 883 bytes

**Engine execution time:** 387 ms

Five records were retrieved successfully.

Example:

| Branch ID | Branch Name | City | Transactions | Units Sold | Revenue |
|-----------|-------------|------|-------------:|-----------:|--------:|
| BR001 | PharmaFlow Branch 1 | East Kirstymouth | 1210 | 9384 | 149224.53 |
| BR002 | PharmaFlow Branch 2 | Lake Dawn | 1236 | 9684 | 154901.18 |
| BR003 | PharmaFlow Branch 3 | Youngmouth | 1303 | 9959 | 161777.80 |

### 2. Medicine Revenue

```sql
SELECT *
FROM pharmaflow_analytics.medicine_revenue
LIMIT 5;
```

**Result:** SUCCEEDED

**Data scanned:** 1,238 bytes

**Engine execution time:** 370 ms

Five records were retrieved successfully.

| Medicine ID | Medicine | Units Sold | Revenue |
|-------------|----------|-----------:|--------:|
| MED001 | Paracetamol 500mg - Pack 1 | 2673 | 6254.82 |
| MED004 | Vitamin C 1000mg - Pack 4 | 2804 | 12365.64 |
| MED005 | Aspirin 75mg - Pack 5 | 2678 | 6855.68 |
| MED002 | Ibuprofen 200mg - Pack 2 | 2366 | 22950.20 |
| MED003 | Cetirizine 10mg - Pack 3 | 2661 | 69638.37 |

### 3. Supplier Spend

```sql
SELECT *
FROM pharmaflow_analytics.supplier_spend
LIMIT 5;
```

**Result:** SUCCEEDED

**Data scanned:** 1,035 bytes

**Engine execution time:** 471 ms

Five records were retrieved successfully.

| Supplier ID | Supplier | Orders | Units Ordered | Total Cost |
|-------------|----------|-------:|--------------:|-----------:|
| SUP001 | Griffiths, Cox and Smith Pharma | 249 | 67060 | 696343.21 |
| SUP004 | Kaur, Quinn and Wright Pharma | 236 | 61040 | 598296.19 |
| SUP005 | White-Stevens Pharma | 266 | 73663 | 749567.65 |
| SUP002 | Cox, Kaur and Wright Pharma | 259 | 65241 | 693017.98 |
| SUP003 | Lowe Inc Pharma | 246 | 60054 | 654152.13 |

## Validation Summary

| Dataset | Query Status | Data Scanned |
|---------|--------------|-------------:|
| branch_revenue | SUCCEEDED | 883 bytes |
| medicine_revenue | SUCCEEDED | 1,238 bytes |
| supplier_spend | SUCCEEDED | 1,035 bytes |
| **Total** | **3 successful queries** | **3,156 bytes** |

All three datasets returned actual records from Amazon S3 through Athena.

## Security and Cost Controls

The project uses:

- IAM Identity Center SSO authentication
- A dedicated `PharmaFlowDeveloper` permission set
- Scoped Glue and Athena permissions
- A dedicated Athena workgroup
- SSE-S3 encryption for query results
- A 10 MiB per-query data scan cutoff
- AWS Budget alerts at a $5 monthly threshold
- Terraform state and credential exclusions from Git

Athena and other AWS services may incur charges. Budget alerts do not enforce a hard spending cap.

Terraform state files and AWS credentials must never be committed to the public repository.

## Engineering Skills Demonstrated

- Python ETL and medallion data architecture
- Cloud-based Parquet data storage
- AWS Glue Data Catalog configuration
- Amazon Athena serverless SQL analytics
- Terraform infrastructure as code
- IAM Identity Center and AWS CLI
- SQL query validation and performance measurement
- Cloud security and cost awareness

## Conclusion

The PharmaFlow AWS analytics integration was successfully deployed and validated.

Three curated Gold-layer Parquet datasets were registered in AWS Glue and queried using Amazon Athena.

The successful execution and retrieval of results from all three tables demonstrates a working S3-to-Glue-to-Athena analytics workflow.
