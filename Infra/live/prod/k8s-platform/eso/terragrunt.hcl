# External Secrets Operator deployment for production
include "root" {
  path   = "${get_repo_root()}/infra/live/terragrunt.hcl"
  expose = true
}
terraform {
  source = "${get_repo_root()}/infra/modules/eks-addons/eso"
}

generate "k8s_provider" {
  path      = "k8s_provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
data "aws_eks_cluster_auth" "this" {
  name = "${dependency.eks.outputs.cluster_name}"
}

provider "helm" {
  kubernetes= {
    host                   = "${dependency.eks.outputs.cluster_endpoint}"
    cluster_ca_certificate = base64decode("${dependency.eks.outputs.cluster_certificate_authority_data}")
    token                  = data.aws_eks_cluster_auth.this.token
  }
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
    eso_irsa_role_arn = "arn:aws:iam::123456789012:role/eso-irsa"
  }
  mock_outputs_allowed_terraform_commands = ["validate", "plan","init"]
}

dependency "vpc" {
  config_path = "../../vpc"
  mock_outputs = {
    vpc_id = "vpc-12345678"
  }
  mock_outputs_allowed_terraform_commands = ["validate", "plan","init"]
}

inputs = {
  eks_cluster_id    = dependency.eks.outputs.cluster_name
  eso_irsa_role_arn = dependency.eks.outputs.eso_irsa_role_arn
  
  # Production configuration
  chart_version  = "0.10.4"
  replica_count  = 2
  cpu_request    = "50m"
  memory_request = "64Mi"
  cpu_limit      = "200m"
  memory_limit   = "256Mi"
}
