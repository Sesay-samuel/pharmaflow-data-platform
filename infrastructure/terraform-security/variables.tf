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
