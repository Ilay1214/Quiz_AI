terraform {
    source = "${get_repo_root()}/infra/modules/ecr"
}

include "root" {
  path   = "${get_repo_root()}/infra/live/terragrunt.hcl"
  expose = true
}
inputs = {
    environment = include.root.locals.environment
    project_name = include.root.locals.project
    ecr_names = ["prod-frontend", "prod-backend"]
}