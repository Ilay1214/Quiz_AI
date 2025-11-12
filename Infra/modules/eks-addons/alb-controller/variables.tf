variable "release_name" {
  description = "Helm release name for AWS Load Balancer Controller"
  type = string
  default = "aws-load-balancer-controller"
}

variable "chart_version" {
  description = "AWS Load Balancer Controller Helm chart version"
  type = string
  default = "1.7.1"
}

variable "namespace" {
  description = "Namespace for AWS Load Balancer Controller"
  type = string
  default = "kube-system"
}

variable "cluster_name" {
  description = "EKS cluster name"
  type = string
}

variable "aws_region" {
  description = "AWS region"
  type = string
}

variable "vpc_id" {
  description = "VPC ID where the cluster is deployed"
  type = string
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs for ALB deployment"
  type = list(string)
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for internal ALB deployment"
  type = list(string)
}

variable "alb_controller_irsa_role_arn" {
  description = "IAM role ARN for ALB Controller IRSA"
  type = string
}

variable "eks_cluster_id" {
  description = "EKS cluster ID/name"
  type = string
}

variable "replica_count" {
  description = "Number of ALB controller replicas"
  type = number
  default = 2
}

variable "cpu_request" {
  description = "CPU request for ALB controller pods"
  type = string
  default = "100m"
}

variable "memory_request" {
  description = "Memory request for ALB controller pods"
  type = string
  default = "128Mi"
}
