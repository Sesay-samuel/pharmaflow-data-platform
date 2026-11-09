
# PharmaFlow PostgreSQL RDS database
resource "aws_db_instance" "pharmaflow" {
  identifier = "pharmaflow-postgres-dev"

  engine         = "postgres"
  engine_version = "16.14"
  instance_class = var.db_instance_class

  allocated_storage = var.db_allocated_storage
  storage_type      = "gp3"
  storage_encrypted = true

  db_name  = var.db_name
  username = var.db_username

  # AWS manages the master password in Secrets Manager.
  # No password is hardcoded in Terraform.
  manage_master_user_password = true

  # Networking
  db_subnet_group_name = aws_db_subnet_group.pharmaflow.name

  vpc_security_group_ids = [
    aws_security_group.rds.id
  ]

  publicly_accessible = false
  multi_az            = false

  # Development environment settings
  backup_retention_period = 1
  deletion_protection     = false
  skip_final_snapshot     = true

  # Avoid automatic major-version upgrades
  auto_minor_version_upgrade = true

  tags = {
    Name        = "pharmaflow-postgres-dev"
    Environment = "Development"
  }
}
