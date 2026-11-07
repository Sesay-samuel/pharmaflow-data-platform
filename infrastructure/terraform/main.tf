
variable "lambda_function_names" {
  description = "Existing Lambda functions to monitor"
  type        = list(string)
  default     = []
}

resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  for_each = toset(var.lambda_function_names)

  alarm_name        = "${var.project_name}-${var.environment}-${each.value}-errors"
  alarm_description = "Detects Lambda execution errors"

  namespace   = "AWS/Lambda"
  metric_name = "Errors"
  statistic   = "Sum"

  period              = 300
  evaluation_periods  = 1
  threshold           = 0
  comparison_operator = "GreaterThanThreshold"

  treat_missing_data = "notBreaching"

  dimensions = {
    FunctionName = each.value
  }

  alarm_actions = [
    aws_sns_topic.pharmaflow_alerts.arn
  ]

}

resource "aws_sns_topic" "pharmaflow_alerts" {
  name = "pharmaflow-dev-monitoring-alerts"
}


data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "sns_cloudwatch" {
  statement {
    sid    = "AllowCloudWatchAlarmPublishing"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["cloudwatch.amazonaws.com"]
    }

    actions = ["SNS:Publish"]

    resources = [
      aws_sns_topic.pharmaflow_alerts.arn
    ]

    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }

    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values = [
        "arn:aws:cloudwatch:${var.aws_region}:${data.aws_caller_identity.current.account_id}:alarm:pharmaflow-dev-*"
      ]
    }
  }

  statement {
    sid    = "AllowAccountOwnerSNSManagement"
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }

    actions = [
      "SNS:GetTopicAttributes",
      "SNS:SetTopicAttributes",
      "SNS:Subscribe",
      "SNS:ListSubscriptionsByTopic",
      "SNS:Publish",
      "SNS:DeleteTopic"
    ]

    resources = [
      aws_sns_topic.pharmaflow_alerts.arn
    ]
  }
}

resource "aws_sns_topic_policy" "pharmaflow_alerts" {
  arn    = aws_sns_topic.pharmaflow_alerts.arn
  policy = data.aws_iam_policy_document.sns_cloudwatch.json
}


resource "aws_budgets_budget" "pharmaflow_monthly" {
  name         = "pharmaflow-monthly-budget"
  budget_type  = "COST"
  limit_amount = "7"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = [var.budget_alert_email]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = [var.budget_alert_email]
  }
}
