
resource "aws_iam_policy" "eso" {
  name   = "${local.env_sanitized}-eso-read-secrets"
  policy = data.aws_iam_policy_document.eso.json
}


resource "aws_iam_policy" "github_oidc_ecr_policy" {
  name        = "${local.env_sanitized}GitHubOidcEcrPolicy"
  description = "Policy to allow GitHub Actions to push to ECR"
  policy      = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:DescribeRepositories",
          "ecr:CreateRepository"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "github_oidc_ecr_attachment" {
  role       = aws_iam_role.github_oidc_role.name
  policy_arn = aws_iam_policy.github_oidc_ecr_policy.arn
}