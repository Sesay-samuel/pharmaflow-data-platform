locals {
  gold_path = "s3://${var.data_bucket}/gold"
}

resource "aws_glue_catalog_database" "analytics" {
  name = "pharmaflow_analytics"
}

resource "aws_glue_catalog_table" "branch_revenue" {
  name          = "branch_revenue"
  database_name = aws_glue_catalog_database.analytics.name
  table_type    = "EXTERNAL_TABLE"

  parameters = {
    classification = "parquet"
    EXTERNAL       = "TRUE"
  }

  storage_descriptor {
    location      = "${local.gold_path}/branch_revenue/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "branch_id"
      type = "string"
    }
    columns {
      name = "branch_name"
      type = "string"
    }
    columns {
      name = "city"
      type = "string"
    }
    columns {
      name = "transactions"
      type = "bigint"
    }
    columns {
      name = "units_sold"
      type = "bigint"
    }
    columns {
      name = "revenue"
      type = "double"
    }
  }
}

resource "aws_glue_catalog_table" "medicine_revenue" {
  name          = "medicine_revenue"
  database_name = aws_glue_catalog_database.analytics.name
  table_type    = "EXTERNAL_TABLE"

  parameters = {
    classification = "parquet"
    EXTERNAL       = "TRUE"
  }

  storage_descriptor {
    location      = "${local.gold_path}/medicine_revenue/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "medicine_id"
      type = "string"
    }
    columns {
      name = "medicine_name"
      type = "string"
    }
    columns {
      name = "units_sold"
      type = "bigint"
    }
    columns {
      name = "revenue"
      type = "double"
    }
  }
}

resource "aws_glue_catalog_table" "supplier_spend" {
  name          = "supplier_spend"
  database_name = aws_glue_catalog_database.analytics.name
  table_type    = "EXTERNAL_TABLE"

  parameters = {
    classification = "parquet"
    EXTERNAL       = "TRUE"
  }

  storage_descriptor {
    location      = "${local.gold_path}/supplier_spend/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "supplier_id"
      type = "string"
    }
    columns {
      name = "supplier_name"
      type = "string"
    }
    columns {
      name = "orders"
      type = "bigint"
    }
    columns {
      name = "units_ordered"
      type = "bigint"
    }
    columns {
      name = "total_cost"
      type = "double"
    }
  }
}

resource "aws_athena_workgroup" "pharmaflow" {
  name = "pharmaflow-analytics"

  configuration {
    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = true
    bytes_scanned_cutoff_per_query     = 10485760

    result_configuration {
      output_location = "s3://${var.data_bucket}/athena-results/"

      encryption_configuration {
        encryption_option = "SSE_S3"
      }
    }
  }
}
