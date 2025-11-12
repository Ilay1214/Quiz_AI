# infra/live/prod/k8s/argocd/terragrunt.hcl
include "root" {
  path   = "${get_repo_root()}/infra/live/terragrunt.hcl"
  expose = true
}

locals {
  raw_environment = try(include.root.locals.environment, "prod")
  environment = (local.raw_environment == "" || local.raw_environment == "/") ? "prod" : local.raw_environment
  env_sanitized = replace(replace(replace(local.environment, " ", "-"), "/", "-"), "\\", "-")
}

dependency "eks" {
  config_path  = "../../eks"   
  mock_outputs = {
    cluster_name = "prod-eks"
    cluster_endpoint = "https://prod-eks-endpoint"
    cluster_certificate_authority_data = "bW9jay1jYS1kYXRh"
  }
  mock_outputs_allowed_terraform_commands = ["validate", "plan","init"]
}

generate "provider_k8s" {
  path      = "provider_k8s.generated.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF


data "aws_eks_cluster_auth" "this" {
  name = "${dependency.eks.outputs.cluster_name}"
}

provider "kubernetes" {
  host = "${dependency.eks.outputs.cluster_endpoint}"
  cluster_ca_certificate = base64decode("${dependency.eks.outputs.cluster_certificate_authority_data}")
  token  = data.aws_eks_cluster_auth.this.token
}

provider "helm" {
  kubernetes = {
    host = "${dependency.eks.outputs.cluster_endpoint}"
    cluster_ca_certificate = base64decode("${dependency.eks.outputs.cluster_certificate_authority_data}")
    token  = data.aws_eks_cluster_auth.this.token
    load_config_file  = false
  }
}
EOF
}

terraform {
  source = "${get_repo_root()}/infra/modules/argocd"
}

dependencies {
  paths = [
    "../../k8s-platform/alb-controller"  # Wait for ALB controller to be ready
  ]
}

inputs = {
  environment = local.env_sanitized
  enable_apps  = false  # Don't create apps here, just install ArgoCD
  app_manifest_path  = ""
  app_manifest_paths = []
}
