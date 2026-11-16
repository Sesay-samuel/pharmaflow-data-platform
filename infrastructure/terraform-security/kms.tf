data "aws_caller_identity" "current" {}

data "aws_partition" "current" {}

data "aws_iam_policy_document" "kms_key_policy" {
  statement {
    sid    = "EnableAccountIAMPolicies"
    effect = "Allow"

    principals {
      type = "AWS"
      identifiers = [
        "arn:${data.aws_partition.current.partition}:iam::${data.aws_caller_identity.current.account_id}:root"
      ]
    }

    actions   = ["kms:*"]
    resources = ["*"]
  }
}

resource "aws_kms_key" "pharmaflow" {
  description             = "PharmaFlow development encryption key"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  policy = data.aws_iam_policy_document.kms_key_policy.json

  tags = {
    Name = "${var.project_name}-${var.environment}-key"
  }
}

resource "aws_kms_alias" "pharmaflow" {
  name          = "alias/${var.project_name}-${var.environment}-data"
  target_key_id = aws_kms_key.pharmaflow.key_id
}
