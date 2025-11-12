

variable "enable_k8s" {
  type    = bool
  default = true
  }

variable "create_crd_resources" {
  description = "Whether to create CRD-dependent resources (ClusterSecretStore, ExternalSecret). Set to false on first run, then true after External Secrets Operator is installed."
  type        = bool
  default     = false
}

variable "manage_namespaces" {
  description = "Whether this module should create namespaces. Set to false if namespaces are managed externally (e.g., by Argo CD)."
  type        = bool
  default     = false
}

variable "enable_aws_load_balancer_controller" {
  description = "Install AWS Load Balancer Controller via Helm"
  type        = bool
  default     = false
}

variable "alb_controller_irsa_role_arn" {
  type = string
  default  = null
}

variable "cluster_name" {
  type = string
  default  = null
}

variable "enable_ingress_nginx" {
  type = bool
  default  = false
}

variable "nginx_namespace" {
  type = string
  default  = "ingress-nginx"
}

variable "nginx_service_name" {
  type = string
  default  = "ingress-nginx-controller"
}

variable "enable_edge_alb_to_nginx" {
  type = bool
  default  = false
}

variable "edge_ingress_annotations" {
  type = map(string)
  default  = {}
}

variable "create_alb_ingress_class" {
  type = bool
  default = true
}