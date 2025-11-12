data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "eso" {
  statement {
    sid     = "SecretsManagerRead"
    effect  = "Allow"
    actions = [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret",
      "secretsmanager:ListSecrets"
    ]
    resources = var.allowed_secret_arns  
  }
}
