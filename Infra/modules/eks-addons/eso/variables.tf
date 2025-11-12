variable "release_name" {
  description = "Helm release name for External Secrets Operator"
  type = string
  default = "external-secrets"
}

variable "chart_version" {
  description = "External Secrets Operator Helm chart version"
  type = string
  default = "0.10.4"
}

variable "namespace" {
  description = "Namespace for External Secrets Operator"
  type = string
  default = "external-secrets"
}

variable "eso_irsa_role_arn" {
  description = "IAM role ARN for External Secrets Operator IRSA"
  type = string
}

variable "eks_cluster_id" {
  description = "EKS cluster ID/name"
  type = string
}

variable "replica_count" {
  description = "Number of ESO replicas"
  type = number
  default = 2
}

variable "cpu_request" {
  description = "CPU request for ESO pods"
  type = string
  default = "50m"
}

variable "memory_request" {
  description = "Memory request for ESO pods"
  type = string
  default = "64Mi"
}

variable "cpu_limit" {
  description = "CPU limit for ESO pods"
  type = string
  default = "200m"
}

variable "memory_limit" {
  description = "Memory limit for ESO pods"
  type = string
  default = "256Mi"
}
