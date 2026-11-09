
# ============================================================
# PharmaFlow Data Engineering Platform
# AWS EC2, RDS PostgreSQL, Security Groups and Networking
# Region: eu-west-2
# ============================================================

# ------------------------------------------------------------
# 1. Existing VPC subnets
# ------------------------------------------------------------

data "aws_subnets" "pharmaflow" {
  filter {
    name   = "vpc-id"
    values = [var.vpc_id]
  }
}

# ------------------------------------------------------------
# 2. EC2 Security Group
# ------------------------------------------------------------

resource "aws_security_group" "ec2" {
  name_prefix = "pharmaflow-ec2-"
  description = "Security group for PharmaFlow EC2"
  vpc_id      = var.vpc_id

  tags = {
    Name = "pharmaflow-ec2-sg"
  }
}

# ------------------------------------------------------------
# 3. EC2 outbound HTTPS
# Required for AWS SSM and AWS services
# ------------------------------------------------------------

resource "aws_vpc_security_group_egress_rule" "ec2_https" {
  security_group_id = aws_security_group.ec2.id

  ip_protocol = "tcp"
  from_port   = 443
  to_port     = 443

  cidr_ipv4 = "0.0.0.0/0"

  description = "Allow outbound HTTPS for AWS services"
}

# ------------------------------------------------------------
# 4. EC2 outbound HTTP
# Required for package installation where HTTP is used
# ------------------------------------------------------------

resource "aws_vpc_security_group_egress_rule" "ec2_http" {
  security_group_id = aws_security_group.ec2.id

  ip_protocol = "tcp"
  from_port   = 80
  to_port     = 80

  cidr_ipv4 = "0.0.0.0/0"

  description = "Allow outbound HTTP for package installation"
}

# ------------------------------------------------------------
# 5. EC2 outbound PostgreSQL
# Allow EC2 to communicate with RDS on port 5432
# ------------------------------------------------------------

resource "aws_vpc_security_group_egress_rule" "ec2_postgres" {
  security_group_id = aws_security_group.ec2.id

  ip_protocol = "tcp"
  from_port   = 5432
  to_port     = 5432

  referenced_security_group_id = aws_security_group.rds.id

  description = "Allow PostgreSQL connections from EC2 to RDS"
}

# ------------------------------------------------------------
# 6. RDS Security Group
# ------------------------------------------------------------

resource "aws_security_group" "rds" {
  name_prefix = "pharmaflow-rds-"
  description = "Private PostgreSQL access from PharmaFlow EC2"
  vpc_id      = var.vpc_id

  tags = {
    Name = "pharmaflow-rds-sg"
  }
}

# ------------------------------------------------------------
# 7. RDS inbound PostgreSQL
# Accept connections from PharmaFlow EC2 only
# ------------------------------------------------------------

resource "aws_vpc_security_group_ingress_rule" "rds_postgres" {
  security_group_id = aws_security_group.rds.id

  ip_protocol = "tcp"
  from_port   = 5432
  to_port     = 5432

  referenced_security_group_id = aws_security_group.ec2.id

  description = "Allow PostgreSQL access from PharmaFlow EC2"
}

# ------------------------------------------------------------
# 8. RDS Private Subnet Group
# Uses dedicated private subnets in two availability zones
# ------------------------------------------------------------

resource "aws_db_subnet_group" "pharmaflow" {
  name = "pharmaflow-db-subnet-group"

  subnet_ids = [
    aws_subnet.rds_private_a.id,
    aws_subnet.rds_private_b.id
  ]

  tags = {
    Name = "pharmaflow-db-subnet-group"
  }
}
