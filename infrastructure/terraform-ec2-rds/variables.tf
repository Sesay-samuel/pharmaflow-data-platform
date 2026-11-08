
variable "aws_region" {
  description = "AWS region for PharmaFlow"
  type        = string
  default     = "eu-west-2"
}

variable "aws_profile" {
  description = "AWS CLI profile"
  type        = string
  default     = "pharmaflow-dev"
}

variable "vpc_id" {
  description = "Existing AWS VPC"
  type        = string
  default     = "vpc-047db759588adf4a2"
}

variable "ec2_instance_type" {
  description = "EC2 instance size"
  type        = string
  default     = "t3.micro"
}

variable "db_instance_class" {
  description = "RDS PostgreSQL instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_name" {
  description = "PharmaFlow PostgreSQL database name"
  type        = string
  default     = "pharmacy_db"
}

variable "db_username" {
  description = "PostgreSQL master username"
  type        = string
  default     = "pharmacy_user"
}

variable "db_allocated_storage" {
  description = "RDS storage in GiB"
  type        = number
  default     = 20
}
