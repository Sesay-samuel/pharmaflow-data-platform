from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import (
    StructType, StructField, StringType,
    IntegerType, DecimalType
)

INPUT = "/opt/project/data/bronze/retail_sales.csv"
OUTPUT = "/opt/project/data/spark/silver/retail_sales"

schema = StructType([
    StructField("sale_id", StringType(), True),
    StructField("sale_date", StringType(), True),
    StructField("branch_id", StringType(), True),
    StructField("medicine_id", StringType(), True),
    StructField("quantity", StringType(), True),
    StructField("unit_price", StringType(), True),
    StructField("total_amount", StringType(), True),
])

def transform_sales(df):
    prepared = (
        df.select(
            F.trim("sale_id").alias("sale_id"),
            F.to_date(F.trim("sale_date"), "yyyy-MM-dd").alias("sale_date"),
            F.trim("branch_id").alias("branch_id"),
            F.trim("medicine_id").alias("medicine_id"),
            F.trim("quantity").cast(IntegerType()).alias("quantity"),
            F.trim("unit_price").cast(DecimalType(12, 2)).alias("unit_price"),
        )
    )

    valid = prepared.filter(
        F.col("sale_id").isNotNull()
        & (F.col("sale_id") != "")
        & F.col("sale_date").isNotNull()
        & F.col("branch_id").isNotNull()
        & (F.col("branch_id") != "")
        & F.col("medicine_id").isNotNull()
        & (F.col("medicine_id") != "")
        & (F.col("quantity") > 0)
        & (F.col("unit_price") >= 0)
    )

    # Keep only sale IDs with one distinct valid record.
    # Conflicting duplicates are excluded rather than selected arbitrarily.
    unique_rows = valid.dropDuplicates()
    counts = unique_rows.groupBy("sale_id").count()

    unique_ids = counts.filter(F.col("count") == 1).select("sale_id")

    clean = unique_rows.join(unique_ids, "sale_id", "inner")

    return clean.withColumn(
        "total_amount",
        (F.col("quantity") * F.col("unit_price")).cast(DecimalType(18, 2))
    ).select(
        "sale_id", "sale_date", "branch_id",
        "medicine_id", "quantity", "unit_price", "total_amount"
    )

def main():
    spark = (
        SparkSession.builder
        .appName("PharmaFlow-Retail-Silver")
        .master("local[2]")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )

    try:
        spark.sparkContext.setLogLevel("ERROR")

        bronze = spark.read.option("header", "true").schema(schema).csv(INPUT)
        silver = transform_sales(bronze)

        bronze_count = bronze.count()
        silver_count = silver.count()

        print("BRONZE RECORDS:", bronze_count)
        print("SILVER RECORDS:", silver_count)
        print("REJECTED OR DEDUPLICATED:", bronze_count - silver_count)

        silver.printSchema()
        silver.show(5, truncate=False)

        silver.write.mode("overwrite").parquet(OUTPUT)

        print("SILVER PARQUET WRITE SUCCESSFUL")
        print("OUTPUT:", OUTPUT)

    finally:
        spark.stop()

if __name__ == "__main__":
    main()
