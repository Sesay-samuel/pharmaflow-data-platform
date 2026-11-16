from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import DecimalType

BASE = "/opt/project/data/spark"
SILVER = f"{BASE}/silver/retail_sales"
GOLD = f"{BASE}/gold"

def build_gold(sales):
    branch_revenue = (
        sales.groupBy("branch_id")
        .agg(
            F.count("*").alias("transactions"),
            F.sum("quantity").alias("units_sold"),
            F.sum("total_amount").cast(
                DecimalType(20, 2)
            ).alias("revenue")
        )
        .orderBy(F.desc("revenue"))
    )

    medicine_revenue = (
        sales.groupBy("medicine_id")
        .agg(
            F.sum("quantity").alias("units_sold"),
            F.sum("total_amount").cast(
                DecimalType(20, 2)
            ).alias("revenue")
        )
        .orderBy(F.desc("revenue"))
    )

    return branch_revenue, medicine_revenue

def main():
    spark = (
        SparkSession.builder
        .appName("PharmaFlow-Gold-Analytics")
        .master("local[2]")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )

    try:
        spark.sparkContext.setLogLevel("ERROR")

        sales = spark.read.parquet(SILVER)

        branch, medicine = build_gold(sales)

        print("SILVER RECORDS:", sales.count())

        print("BRANCH REVENUE")
        branch.show(10, truncate=False)

        print("MEDICINE REVENUE")
        medicine.show(10, truncate=False)

        branch.write.mode("overwrite").parquet(
            f"{GOLD}/branch_revenue"
        )

        medicine.write.mode("overwrite").parquet(
            f"{GOLD}/medicine_revenue"
        )

        print("GOLD ANALYTICS WRITE SUCCESSFUL")

    finally:
        spark.stop()

if __name__ == "__main__":
    main()
