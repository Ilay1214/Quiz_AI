terraform {
    source = "${get_repo_root()}/infra/modules/IAM"
}

include "root" {
  path   = "${get_repo_root()}/infra/live/terragrunt.hcl"
  expose = true
}
locals {
    region = include.root.locals.aws_region
    account_id = include.root.locals.aws_account_id
}

inputs = {
    environment = include.root.locals.environment
    project_name = include.root.locals.project
    github_repo = include.root.locals.github_repo

    allowed_secret_arns = [
        "arn:aws:secretsmanager:${local.region}:${local.account_id}:secret:*"
]
}
