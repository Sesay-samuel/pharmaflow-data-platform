
# Read access to the RDS-managed master secret
data "aws_iam_policy_document" "rds_secret_access" {
  statement {
    sid = "ReadPharmaFlowRDSSecret"

    effect = "Allow"

    actions = [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret"
    ]

    resources = [
      aws_db_instance.pharmaflow.master_user_secret[0].secret_arn
    ]
  }
}

# Attach the policy to the existing EC2 role
resource "aws_iam_role_policy" "rds_secret_access" {
  name = "pharmaflow-rds-secret-access"

  role = aws_iam_role.ec2_ssm.id

  policy = data.aws_iam_policy_document.rds_secret_access.json
}
