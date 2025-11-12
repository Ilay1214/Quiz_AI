variable "secret_store_name" {
  description = "Name of the ClusterSecretStore"
  type = string
  default = "aws-secrets-manager"
}

variable "aws_region" {
  description = "AWS region for Secrets Manager"
  type = string
}

variable "eso_service_account" {
  description = "ESO service account name"
  type = string
  default = "external-secrets"
}

variable "eso_namespace" {
  description = "ESO namespace"
  type = string
  default = "external-secrets"
}

variable "eso_crds_ready" {
  description = "Dependency on ESO CRDs being ready"
  type = string
}
