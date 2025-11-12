resource "aws_iam_role" "github_oidc_role" {
  name               = "${local.env_sanitized}GitHubOidcRole"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "sts:AssumeRoleWithWebIdentity"
        Principal = {
          Federated = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:oidc-provider/token.actions.githubusercontent.com"

        }
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = [
              "sts.amazonaws.com"
            ]
          }
          StringLike = {
            "token.actions.githubusercontent.com:sub" = [
              "repo:${var.github_repo}/*"
            ]
          }
        }
      }
    ]
  })
}

