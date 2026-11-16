data "aws_iam_policy_document" "database_secret_read" {
  statement {
    sid    = "ReadPharmaFlowDatabaseSecret"
    effect = "Allow"

    actions = [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret"
    ]

    resources = [
      aws_secretsmanager_secret.database.arn
    ]
  }
}

resource "aws_iam_policy" "database_secret_read" {
  name = "${var.project_name}-${var.environment}-database-secret-read"

  description = "Read-only access to PharmaFlow database secret"

  policy = data.aws_iam_policy_document.database_secret_read.json
}
