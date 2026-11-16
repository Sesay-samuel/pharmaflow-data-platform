resource "aws_secretsmanager_secret" "database" {
  name = "${var.project_name}/${var.environment}/database"

  description = "PharmaFlow database credentials"

  recovery_window_in_days = 30

  tags = {
    Name        = "pharmaflow-database-secret"
    Environment = var.environment
  }
}
