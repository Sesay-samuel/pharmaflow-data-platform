
variable "aws_region" {
  description = "AWS deployment region"
  type        = string
  default     = "eu-west-2"
}

variable "aws_profile" {
  description = "AWS CLI profile"
  type        = string
  default     = "pharmaflow-dev"
}

variable "project_name" {
  description = "Project identifier"
  type        = string
  default     = "pharmaflow"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "s3_bucket_name" {
  description = "Existing PharmaFlow S3 bucket"
  type        = string
  default     = "pharmaflow-data-673502297238-eu-west-2"
}


variable "budget_alert_email" {
  description = "Email address for AWS budget alerts"
  type        = string
  sensitive   = true
}
