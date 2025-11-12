include "root" {
  path   = "${get_repo_root()}/infra/live/terragrunt.hcl"
  expose = true
}

dependency "eks" { 
  config_path = "../eks"
  mock_outputs = {
    cluster_name = "mock-cluster"
    cluster_endpoint = "https://mock-cluster-endpoint"
    cluster_certificate_authority_data = "bW9jay1jYS1kYXRh"
  }
  mock_outputs_allowed_terraform_commands = ["validate", "plan","init"]
}


generate "provider_k8s" {
  path = "provider_k8s.generated.tf"
  if_exists = "overwrite_terragrunt"
  contents = <<-EOF
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
    host = "${dependency.eks.outputs.cluster_endpoint}"
    token = data.aws_eks_cluster_auth.this.token
    insecure = true
  }

  provider "helm" {
    kubernetes = {
      host = "${dependency.eks.outputs.cluster_endpoint}"
      token = data.aws_eks_cluster_auth.this.token
      insecure = true
      load_config_file = false
    }
  }
  EOF
}

terraform { source = "${get_repo_root()}/infra/modules/eso-aws-config" }

inputs = { 
  enable_k8s  = true 
  region  = "eu-central-1"
  create_cluster_secret_store = false
  secret_store_name = "aws-secrets-manager"
  sa_name  = "external-secrets"
  sa_namespace = "external-secrets"
  mysql_ca_property  = "MYSQL_CA_CERT"
  namespaces = { 
    prod = { 
      name = "quiz-ai-prod"
      remote_key = "prod/quiz-ai"
    } 
  } 
}

dependencies {
  paths = [
    "../k8s-platform/eso",
    "../k8s-platform/cluster-secret-store"
  ]
}