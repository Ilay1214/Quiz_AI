terraform {
  required_version = ">= 1.3.0"
  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = ">= 2.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.0"
    }
  }
}

# External Secrets Operator Helm Release
resource "helm_release" "external_secrets" {
  name = var.release_name
  repository = "https://charts.external-secrets.io"
  chart = "external-secrets"
  version = var.chart_version
  namespace = var.namespace

  create_namespace = true
  wait = true
  wait_for_jobs = true
  timeout = 600

  values = [
    templatefile("${path.module}/values.yaml.tpl", {
      eso_irsa_role_arn = var.eso_irsa_role_arn
      replica_count = var.replica_count
      cpu_request = var.cpu_request
      memory_request = var.memory_request
      cpu_limit = var.cpu_limit
      memory_limit = var.memory_limit
    })
  ]

  depends_on = [var.eks_cluster_id]
}

# Wait for CRDs to be fully install 
resource "time_sleep" "wait_for_crds" {
  depends_on = [helm_release.external_secrets]
  create_duration = "60s"
}
