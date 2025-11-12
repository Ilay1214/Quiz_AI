locals {
  primary_ng = {
    "${var.environment}-eks-node-group" = {
      kubernetes_version = var.kubernetes_version
      instance_types = var.instance_types
      min_size = var.min_size
      capacity_type = var.capacity_type
      ami_type  = var.ami_type

      tags = {
        "k8s.io/cluster-autoscaler/${var.environment}-eks-cluster" = "owned"
        "k8s.io/cluster-autoscaler/enabled"                        = "true"
      }

      labels = {
        capacity_type = lower(var.capacity_type)
        node_group    = "primary"
      }
      taints = var.capacity_type == "SPOT" ? {
        spot = {
          key    = "spot"
          value  = "true"
          effect = "NO_SCHEDULE"
        }
      } : null
    }
  }

  spot_ng = var.enable_spot_group ? {
    "${var.environment}-eks-spot-group" = {
      kubernetes_version = var.kubernetes_version
      instance_types = coalesce(var.spot_instance_types, ["t3.large", "t3a.large"])
      min_size = coalesce(var.spot_min_size, 0)
      max_size = coalesce(var.spot_max_size, 5)
      desired_size  = coalesce(var.spot_desired_size, 1)
      capacity_type  = "SPOT"
      ami_type = var.ami_type

      tags = {
        "k8s.io/cluster-autoscaler/${var.environment}-eks-cluster" = "owned"
        "k8s.io/cluster-autoscaler/enabled"                        = "true"
      }

      labels = {
        capacity_type = "spot"
        node_group    = "spot"
      }

      taints = {
        spot = {
          key    = "spot"
          value  = "true"
          effect = "NO_SCHEDULE"
        }
      }
    }
  } : {}
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "21.6.1"

  name = "${var.environment}-eks-cluster"
  kubernetes_version = var.kubernetes_version
  enable_irsa = true
  endpoint_public_access = true
  endpoint_private_access = true
  endpoint_public_access_cidrs = var.api_public_cidrs
  control_plane_subnet_ids = var.private_subnets

  create_kms_key  = true
  kms_key_enable_default_policy = true
  enable_cluster_creator_admin_permissions = true

  vpc_id     = var.vpc_id
  subnet_ids = var.private_subnets

  addons = {
    coredns = {
      configuration_values = jsonencode({
        replicaCount = 1
        resources = {
          limits = { cpu = "100m", memory = "128Mi" }
          requests = { cpu = "100m", memory = "70Mi" }
        }
      })
    }
    eks-pod-identity-agent = { before_compute = true }
    kube-proxy = {}
    vpc-cni = { before_compute = true }
  }

  eks_managed_node_groups = merge(local.primary_ng, local.spot_ng)
}

module "eso_irsa_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-assumable-role-with-oidc"
  version = "~> 5.46"

  create_role  = true
  role_name    = "${var.environment}-eso-irsa"
  provider_url = replace(module.eks.cluster_oidc_issuer_url, "https://", "")
  role_policy_arns = [var.eso_policy_arn]
  oidc_fully_qualified_subjects = [
    "system:serviceaccount:external-secrets:external-secrets",
  ]
}

module "cluster_autoscaler_irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.6"

  role_name = "${var.environment}-cluster-autoscaler-irsa"
  attach_cluster_autoscaler_policy  = true
  cluster_autoscaler_cluster_names  = [module.eks.cluster_name]
  oidc_providers = {
    main = {
      provider_arn = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:cluster-autoscaler"]
    }
  }
}

module "alb_controller_irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.6"

  role_name = "${var.environment}-aws-load-balancer-controller-irsa"
  attach_load_balancer_controller_policy = true

  oidc_providers = {
    main = {
      provider_arn = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:aws-load-balancer-controller"]
    }
  }
}
