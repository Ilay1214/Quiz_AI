locals {
  project = "quiz-ai"
  aws_region  = "eu-central-1"
  rel_path_raw = path_relative_to_include()
  rel_path_norm  = trim(replace(local.rel_path_raw, "\\", "/"), "/")
  environment = split(local.rel_path_norm != "" ? local.rel_path_norm : "unknown", "/")[0]
  aws_account_id = "505825010815"
  github_repo = "Ilay1214/quiz_ai_infra"
}


remote_state {
  backend = "s3"
  config = {
    bucket = "tf-state-${local.project}"
    key = "${local.rel_path_norm != "" ? local.rel_path_norm : local.environment}/terraform.tfstate"
    region = local.aws_region
    dynamodb_table = "${local.project}-terraform-lock"
    encrypt = true
  }
}

generate "backend" {
  path      = "backend.generated.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
terraform {
  backend "s3" {}
}
EOF
}

generate "provider" {
  path = "provider.generated.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
provider "aws" {
  region = "${local.aws_region}"
}
EOF
}

inputs = {
  common_tags = {
    Project = local.project
    Environment = local.environment
    ManagedBy = "Terragrunt"
  }
}