terraform {
    source = "${get_parent_terragrunt_dir()}/../modules/vpc"
}
include "root" {
  path = "${get_repo_root()}/infra/live/terragrunt.hcl"
  expose = true
}
locals {
    env = include.root.locals.environment
    project = include.root.locals.project
    cluster_name = "${local.env}-eks-cluster"
    tags = {
     project = include.root.locals.project
     environment = local.env

    }
}

inputs = {
    vpc_cidr = "10.0.0.0/16"
    num_of_azs = 2
    environment = local.env
    common_tags = local.tags
    project_name = include.root.locals.project
    cluster_name = local.cluster_name
}
