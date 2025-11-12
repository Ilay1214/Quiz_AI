terraform {
    source = "${get_parent_terragrunt_dir()}/../modules/vpc"
}
include "root" {
  path = "${get_repo_root()}/infra/live/terragrunt.hcl"
  expose = true
}
locals {
    env = "prod"  # Explicitly set to prod to avoid path parsing issues
    project = include.root.locals.project
    cluster_name = "prod-eks-cluster"  # Explicitly set cluster name
    tags = {
     project = include.root.locals.project
     environment = "prod"

    }
}

inputs = {
    vpc_cidr = "10.0.0.0/16"
    num_of_azs = 3
    environment = local.env
    common_tags = local.tags
    project_name = include.root.locals.project
    cluster_name = local.cluster_name
}
