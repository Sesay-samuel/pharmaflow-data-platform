from decimal import Decimal
from pyspark.sql import SparkSession
from retail_sales_silver import transform_sales

spark = (
    SparkSession.builder
    .appName("PharmaFlow-Spark-Tests")
    .master("local[2]")
    .config("spark.ui.enabled", "false")
    .getOrCreate()
)

try:
    spark.sparkContext.setLogLevel("ERROR")

    columns = [
        "sale_id", "sale_date", "branch_id",
        "medicine_id", "quantity", "unit_price",
        "total_amount"
    ]

    rows = [
        ("S001", "2026-01-01", "BR001", "MED001", "2", "10.50", "999.00"),
        ("S001", "2026-01-01", "BR001", "MED001", "2", "10.50", "999.00"),
        ("S002", "2026-01-01", "BR001", "MED002", "0", "5.00", "0"),
        ("S003", "2026-01-01", "BR002", "MED003", "1", "-3.00", "-3"),
        ("S004", "2026-01-02", "BR002", "MED004", "3", "4.25", "0"),
        ("S005", "2026-01-02", "BR002", "MED005", "1", "7.00", "7"),
        ("S005", "2026-01-02", "BR003", "MED005", "1", "7.00", "7"),
    ]

    source = spark.createDataFrame(rows, columns)
    result = transform_sales(source)

    output = {
        row["sale_id"]: row
        for row in result.collect()
    }

    assert len(output) == 2, "Expected two valid unique sales"
    assert set(output) == {"S001", "S004"}

    assert output["S001"]["total_amount"] == Decimal("21.00")
    assert output["S004"]["total_amount"] == Decimal("12.75")

    assert "S002" not in output
    assert "S003" not in output
    assert "S005" not in output

    print("ALL SPARK TRANSFORMATION TESTS PASSED")

finally:
    spark.stop()
