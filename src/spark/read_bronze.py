from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("PharmaFlow-Bronze-Reader")
    .master("local[2]")
    .config("spark.ui.enabled", "false")
    .getOrCreate()
)

try:
    spark.sparkContext.setLogLevel("ERROR")

    df = (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .csv("/opt/project/data/bronze/retail_sales.csv")
    )

    print("PHARMAFLOW BRONZE SCHEMA")
    df.printSchema()

    print("PHARMAFLOW BRONZE SAMPLE")
    df.show(5, truncate=False)

    print("TOTAL RETAIL SALES RECORDS:", df.count())

finally:
    spark.stop()
