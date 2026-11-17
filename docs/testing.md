
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

## Agentic AI Testing

The PharmaFlow Agentic AI feature includes automated tests for:

- Analytics data retrieval and validation
- Natural-language request routing
- Approved tool execution
- Rejection of unsupported datasets and operations
- MCP response extraction
- AI response cleaning

### Run Agent Tests

```powershell
python -m pytest src/agents/ -v
```

**Verified on 17 November 2026:** 20 tests passed.

### Run Existing Project Tests

```powershell
python -m pytest -q
```

**Verified on 17 November 2026:** 14 tests passed.

### MCP Integration Verification

```powershell
python -m src.agents.test_mcp_client
```

The MCP integration client has successfully connected to the local MCP server, discovered the approved tools, and retrieved pharmacy analytics results.

### Manual AI Dashboard Verification

Run:

```powershell
python -m streamlit run dashboard/ai_app.py
```

The following operations have been manually tested:

- Supplier spending summaries
- Top pharmacy branches by revenue
- Local AI chat interaction

### Current Testing Limitations

The 20 automated agent tests do not fully exercise live Qwen3 inference through the MCP server.

Production-scale load testing, model evaluation, concurrent-user testing and recovery testing remain future improvements.
