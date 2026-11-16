from decimal import Decimal
from pyspark.sql import SparkSession, functions as F

BASE = "/opt/project/data/spark"

spark = (
    SparkSession.builder
    .appName("PharmaFlow-Reconciliation")
    .master("local[2]")
    .config("spark.ui.enabled", "false")
    .getOrCreate()
)

try:
    spark.sparkContext.setLogLevel("ERROR")

    silver = spark.read.parquet(f"{BASE}/silver/retail_sales")
    branch = spark.read.parquet(f"{BASE}/gold/branch_revenue")
    medicine = spark.read.parquet(f"{BASE}/gold/medicine_revenue")

    silver_total = silver.agg(F.sum("total_amount")).first()[0]
    branch_total = branch.agg(F.sum("revenue")).first()[0]
    medicine_total = medicine.agg(F.sum("revenue")).first()[0]

    silver_units = silver.agg(F.sum("quantity")).first()[0]
    branch_units = branch.agg(F.sum("units_sold")).first()[0]
    medicine_units = medicine.agg(F.sum("units_sold")).first()[0]

    transactions = silver.count()
    branch_transactions = branch.agg(
        F.sum("transactions")
    ).first()[0]

    print("SILVER TOTAL:", silver_total)
    print("BRANCH GOLD TOTAL:", branch_total)
    print("MEDICINE GOLD TOTAL:", medicine_total)
    print("SILVER UNITS:", silver_units)
    print("BRANCH UNITS:", branch_units)
    print("MEDICINE UNITS:", medicine_units)
    print("SILVER TRANSACTIONS:", transactions)
    print("BRANCH TRANSACTIONS:", branch_transactions)

    assert silver_total == branch_total == medicine_total
    assert silver_units == branch_units == medicine_units
    assert transactions == branch_transactions == 10000
    assert branch.count() == 8
    assert medicine.count() == 30

    print("ALL SPARK RECONCILIATION CHECKS PASSED")

finally:
    spark.stop()
