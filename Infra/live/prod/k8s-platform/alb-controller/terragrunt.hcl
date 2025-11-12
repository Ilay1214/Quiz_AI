# AWS Load Balancer Controller for production
include "root" {
  path   = "${get_repo_root()}/infra/live/terragrunt.hcl"
  expose = true
}

terraform {
  source = "${get_repo_root()}/infra/modules/eks-addons/alb-controller"
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
    alb_controller_irsa_role_arn = "arn:aws:iam::123456789012:role/alb-controller-irsa"
  }
  mock_outputs_allowed_terraform_commands = ["validate", "plan","init"]
}

dependency "vpc" {
  config_path = "../../vpc"
  mock_outputs = {
    vpc_id = "vpc-000000"
    public_subnets = ["subnet-0000001", "subnet-0000002"]
    private_subnets = ["subnet-0000003", "subnet-0000004"]
  }
  mock_outputs_allowed_terraform_commands = ["validate", "plan","init"]
}

inputs = {
  cluster_name                 = dependency.eks.outputs.cluster_name
  eks_cluster_id               = dependency.eks.outputs.cluster_name
  aws_region                   = "eu-central-1"
  vpc_id                       = dependency.vpc.outputs.vpc_id
  public_subnet_ids            = dependency.vpc.outputs.public_subnets
  private_subnet_ids           = dependency.vpc.outputs.private_subnets
  alb_controller_irsa_role_arn = dependency.eks.outputs.alb_controller_irsa_role_arn
  
  # Production configuration
  chart_version         = "1.7.1"
  replica_count         = 2
  cpu_request           = "100m"
  memory_request        = "128Mi"
}
