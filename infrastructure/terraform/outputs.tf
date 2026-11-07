
output "aws_region" {
  description = "Configured AWS region"
  value       = var.aws_region
}

output "monitored_lambda_functions" {
  description = "Lambda functions monitored by CloudWatch"
  value       = var.lambda_function_names
}

output "cloudwatch_alarm_names" {
  description = "CloudWatch alarms managed by Terraform"
  value = [
    for alarm in aws_cloudwatch_metric_alarm.lambda_errors :
    alarm.alarm_name
  ]
}


output "sns_topic_arn" {
  description = "SNS topic for PharmaFlow monitoring"
  value       = aws_sns_topic.pharmaflow_alerts.arn
}
