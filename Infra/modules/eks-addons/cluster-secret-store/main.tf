terraform {
  required_version = ">= 1.3.0"
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.0"
    }
  }
}

# ClusterSecretStore for AWS Secrets Manager
resource "kubernetes_manifest" "cluster_secret_store" {
  manifest = {
    apiVersion = "external-secrets.io/v1beta1"
    kind = "ClusterSecretStore"
    metadata = {
      name = var.secret_store_name
    }
    spec = {
      provider = {
        aws = {
          service = "SecretsManager"
          region = var.aws_region
          auth = {
            jwt = {
              serviceAccountRef = {
                name = var.eso_service_account
                namespace = var.eso_namespace
              }
            }
          }
        }
      }
    }
  }

  depends_on = [var.eso_crds_ready]
}
