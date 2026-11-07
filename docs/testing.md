
# PharmaFlow Testing and Validation

## Automated Tests

Command:

```powershell
pytest -q
```

Result:

```text
14 passed in 2.40s
```

Verified: 7 November 2026.

## PostgreSQL Validation

Retail sales:

```text
10,000 records
```

Wholesale orders:

```text
3,000 records
```

## Apache Airflow

DAG: `pharmaflow_medallion_pipeline`

Four recorded manual DAG runs completed successfully.

## AWS S3

Verified prefixes:

- audit/
- bronze/
- silver/
- gold/

Verified Gold files:

- api_summary.json
- branch_revenue.parquet
- medicine_revenue.parquet
- supplier_spend.parquet

## Monitoring

- Two CloudWatch Lambda error alarms configured
- SNS topic and CloudWatch publishing policy verified
- SNS test email received successfully

## S3 Security

- Four public-access-block settings enabled
- Default AES256 encryption
- Bucket versioning enabled

## Limitations

The tests verify selected pipeline functions and infrastructure
components. Full production-scale performance, recovery and
end-to-end failure scenarios have not been tested.
```
