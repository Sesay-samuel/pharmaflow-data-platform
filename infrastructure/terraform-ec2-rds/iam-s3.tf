
# Allow EC2 to read PharmaFlow Gold-layer datasets
data "aws_iam_policy_document" "gold_data_access" {
  statement {
    sid    = "ReadPharmaFlowGoldData"
    effect = "Allow"

    actions = [
      "s3:GetObject"
    ]

    resources = [
      "arn:aws:s3:::pharmaflow-data-673502297238-eu-west-2/gold/*"
    ]
  }
}

resource "aws_iam_role_policy" "gold_data_access" {
  name = "pharmaflow-gold-data-read"

  role   = aws_iam_role.ec2_ssm.id
  policy = data.aws_iam_policy_document.gold_data_access.json
}
