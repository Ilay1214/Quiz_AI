
terraform {
  source = "${get_repo_root()}/infra/modules/argocd-apps"
}
include "root" {
  path   = "${get_repo_root()}/infra/live/terragrunt.hcl"
  expose = true
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

generate "provider_k8s" {
  path      = "provider_k8s.generated.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.25.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = ">= 2.11.0"
    }
  }
}

data "aws_eks_cluster_auth" "this" {
  name = "${dependency.eks.outputs.cluster_name}"
}

provider "kubernetes" {
  host  = "${dependency.eks.outputs.cluster_endpoint}"
  cluster_ca_certificate = base64decode("${dependency.eks.outputs.cluster_certificate_authority_data}")
  token = data.aws_eks_cluster_auth.this.token
}

provider "helm" {
  kubernetes {
    host = "${dependency.eks.outputs.cluster_endpoint}"
    cluster_ca_certificate = base64decode("${dependency.eks.outputs.cluster_certificate_authority_data}")
    token   = data.aws_eks_cluster_auth.this.token
  }
}
EOF
}
inputs = {
  app_manifest_paths = [
    # Apps-only configuration - excludes Terraform-managed infrastructure
    "${get_repo_root()}/infra/argocd/prod/apps-only.yaml"
  ]
}

dependencies {
  paths = [
    "../argocd",
    "../../secrets"  # Ensure secrets are created before deploying apps
  ]
}
