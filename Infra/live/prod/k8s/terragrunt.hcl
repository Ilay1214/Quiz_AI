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
    cluster_autoscaler_irsa_role_arn = "arn:aws:iam::111122223333:role/mock-ca-irsa"
  }
  mock_outputs_allowed_terraform_commands = ["validate", "plan","init"]
}

generate "provider_k8s" {
  path = "provider_k8s.generated.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
terraform {
  required_providers {
    kubernetes = { source = "hashicorp/kubernetes", version = ">= 2.25.0" }
    helm  = { source = "hashicorp/helm",       version = ">= 2.11.0" }
  }
}

data "aws_eks_cluster_auth" "this" {
  name = "${dependency.eks.outputs.cluster_name}"
}

provider "kubernetes" {
  host  = "${dependency.eks.outputs.cluster_endpoint}"
  cluster_ca_certificate = base64decode("${dependency.eks.outputs.cluster_certificate_authority_data}")
  token  = data.aws_eks_cluster_auth.this.token
}

provider "helm" {
  kubernetes = {
    host  = "${dependency.eks.outputs.cluster_endpoint}"
    cluster_ca_certificate = base64decode("${dependency.eks.outputs.cluster_certificate_authority_data}")
    token  = data.aws_eks_cluster_auth.this.token
    load_config_file = false
  }
}
EOF
}

generate "cluster_autoscaler" {
  path = "cluster_autoscaler.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<-EOF
resource "kubernetes_service_account" "cluster_autoscaler" {
  metadata {
    name = "cluster-autoscaler"
    namespace = "kube-system"
    annotations = {
      "eks.amazonaws.com/role-arn" = "${dependency.eks.outputs.cluster_autoscaler_irsa_role_arn}"
    }
  }
}

resource "helm_release" "cluster_autoscaler" {
  name = "cluster-autoscaler"
  repository = "https://kubernetes.github.io/autoscaler"
  chart = "cluster-autoscaler"
  namespace  = "kube-system"
  version = "9.29.3"

  set = [
    { name = "autoDiscovery.clusterName", value = "${dependency.eks.outputs.cluster_name}" },
    { name = "awsRegion", value = "${include.root.locals.aws_region}" },
    { name = "rbac.serviceAccount.create",value = "false" },
    { name = "rbac.serviceAccount.name",value = "cluster-autoscaler" },
    { name = "extraArgs.balance-similar-node-groups", value = "true" },
    { name = "extraArgs.skip-nodes-with-system-pods", value = "false" },
    { name = "resources.limits.cpu",value = "100m" },
    { name = "resources.limits.memory", value = "300Mi" }
  ]

  depends_on = [
    kubernetes_service_account.cluster_autoscaler
  ]
}

EOF
}

terraform {
  source = "."
}
