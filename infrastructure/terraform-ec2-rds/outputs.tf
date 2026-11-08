
# EC2 instance information
output "ec2_instance_id" {
  description = "PharmaFlow EC2 instance ID"
  value       = aws_instance.pharmaflow.id
}

output "ec2_public_ip" {
  description = "Public IPv4 address of PharmaFlow EC2"
  value       = aws_instance.pharmaflow.public_ip
}

output "ec2_private_ip" {
  description = "Private IPv4 address of PharmaFlow EC2"
  value       = aws_instance.pharmaflow.private_ip
}

# PostgreSQL RDS information
output "rds_endpoint" {
  description = "Private PostgreSQL RDS endpoint"
  value       = aws_db_instance.pharmaflow.endpoint
}

output "rds_address" {
  description = "PostgreSQL RDS hostname"
  value       = aws_db_instance.pharmaflow.address
}

output "rds_port" {
  description = "PostgreSQL RDS port"
  value       = aws_db_instance.pharmaflow.port
}

output "rds_database_name" {
  description = "PharmaFlow database name"
  value       = aws_db_instance.pharmaflow.db_name
}

# Security groups
output "ec2_security_group_id" {
  description = "EC2 security group ID"
  value       = aws_security_group.ec2.id
}

output "rds_security_group_id" {
  description = "RDS security group ID"
  value       = aws_security_group.rds.id
}
