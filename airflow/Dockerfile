
FROM apache/airflow:3.1.7-python3.12

USER airflow

RUN pip install --no-cache-dir \
    "pandas>=2.2,<3" \
    "numpy>=1.26,<3" \
    "Faker>=30,<40" \
    "SQLAlchemy>=2.0,<3" \
    "psycopg[binary]>=3.2,<4" \
    "python-dotenv>=1.0,<2" \
    "pyarrow>=17,<24"\
    "boto3>=1.35,<2"
