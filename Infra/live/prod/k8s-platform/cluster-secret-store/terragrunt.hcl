# ClusterSecretStore for production
include "root" {
  path   = "${get_repo_root()}/infra/live/terragrunt.hcl"
  expose = true
}
terraform {
  source = "${get_repo_root()}/infra/modules/eks-addons/cluster-secret-store"
}

generate "k8s_provider" {
  path      = "k8s_provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
data "aws_eks_cluster_auth" "this" {
  name = "${dependency.eks.outputs.cluster_name}"
}

provider "kubernetes" {
  host                   = "${dependency.eks.outputs.cluster_endpoint}"
  cluster_ca_certificate = base64decode("${dependency.eks.outputs.cluster_certificate_authority_data}")
  token                  = data.aws_eks_cluster_auth.this.token
}
EOF
}

dependency "eks" {
  config_path = "../../eks"
  mock_outputs = {
    cluster_name = "prod-eks"
    cluster_endpoint = "https://prod-eks-endpoint"
    cluster_certificate_authority_data = "bW9jay1jYS1kYXRh"
  }
  mock_outputs_allowed_terraform_commands = ["validate", "plan","init"]
}

dependency "eso" {
  config_path = "../eso"
  mock_outputs = {
    service_account = "external-secrets"
    namespace = "external-secrets"
    crds_ready = true
  }
  mock_outputs_allowed_terraform_commands = ["validate", "plan","init"]
}

inputs = {
  secret_store_name   = "aws-secrets-manager"  # Keep the same name apps are using
  aws_region          = "eu-central-1"
  eso_service_account = dependency.eso.outputs.service_account
  eso_namespace       = dependency.eso.outputs.namespace
  eso_crds_ready      = dependency.eso.outputs.crds_ready
}
