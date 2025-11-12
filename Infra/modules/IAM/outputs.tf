output "eso_policy_arn" {
    value = aws_iam_policy.eso.arn
}
output "github_oidc_ecr_policy_arn" {
    value = aws_iam_policy.github_oidc_ecr_policy.arn
}