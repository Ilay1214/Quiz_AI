terraform {
    source = "${get_repo_root()}/infra/modules/eks"
}
include "root" {
  path   = "${get_repo_root()}/infra/live/terragrunt.hcl"
  expose = true
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

provider "kubernetes" {
  host  = try(module.eks.cluster_endpoint, "")
  cluster_ca_certificate = try(base64decode(module.eks.cluster_certificate_authority_data), "")
  
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args = ["eks", "get-token", "--cluster-name", try(module.eks.cluster_name, "")]
  }
}

provider "helm" {
  kubernetes {
    host  = try(module.eks.cluster_endpoint, "")
    cluster_ca_certificate = try(base64decode(module.eks.cluster_certificate_authority_data), "")
    
    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command  = "aws"
      args = ["eks", "get-token", "--cluster-name", try(module.eks.cluster_name, "")]
    }
  }
}
EOF
}

dependency "vpc" {
    config_path = "../vpc"
    mock_outputs = {
        vpc_id  = "vpc-000000"
        private_subnets = ["subnet-0000001", "subnet-0000002"]
    }
    mock_outputs_allowed_terraform_commands = ["validate", "plan", "init", "destroy"]
}
dependency "iam" {
    config_path = "../iam"
    mock_outputs = {
        eso_policy_arn = "arn:aws:iam::111122223333:policy/mock-eso"
    }
    mock_outputs_allowed_terraform_commands = ["validate", "plan", "init", "destroy"]
}

locals {
    env = "dev"
    tags = {
     project = include.root.locals.project
     environment = local.env
     
    }
    is_windows = length(regexall("(?i)windows", get_env("OS", ""))) > 0
    my_ip = chomp(run_cmd("curl", "-s", "https://checkip.amazonaws.com"))
    api_public_cidrs = ["${local.my_ip}/32"]
}

inputs = {
    vpc_id = dependency.vpc.outputs.vpc_id
    private_subnets = dependency.vpc.outputs.private_subnets
    api_public_cidrs = local.api_public_cidrs
    eso_policy_arn = dependency.iam.outputs.eso_policy_arn
    environment = local.env

    #node group settings for primary on-demand group:
    instance_types = ["t3.large"]  
    min_size = 1
    max_size = 2
    desired_size = 1
    capacity_type = "ON_DEMAND"
    ami_type = "AL2_x86_64"
    kubernetes_version = "1.29"
    
    # Enable additional spot instance group for cost optimization
    enable_spot_group = false
    spot_instance_types = ["t3.large", "t3.medium"]
    spot_min_size = 0
    spot_max_size = 0
    spot_desired_size = 0
}
