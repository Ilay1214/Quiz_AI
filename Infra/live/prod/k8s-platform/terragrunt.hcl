# Platform components for production EKS cluster
include "root" {
  path   = "${get_repo_root()}/infra/live/terragrunt.hcl"
  expose = true
}

dependency "eks" {
  config_path = "../eks"
  mock_outputs = {
    cluster_name = "prod-eks"
    cluster_endpoint = "https://prod-eks-endpoint"
    cluster_certificate_authority_data = "bW9jay1jYS1kYXRh"
    cluster_autoscaler_irsa_role_arn = "arn:aws:iam::111122223333:role/mock-ca-irsa"
  }
  mock_outputs_allowed_terraform_commands = ["validate", "plan","init"]
}

# Provider configuration moved to individual child modules
