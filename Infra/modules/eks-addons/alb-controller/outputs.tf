output "namespace" {
  description = "Namespace where ALB Controller is installed"
  value = helm_release.aws_load_balancer_controller.namespace
}

output "release_name" {
  description = "Helm release name"
  value = helm_release.aws_load_balancer_controller.name
}

output "service_account" {
  description = "ALB Controller service account name"
  value = "aws-load-balancer-controller"
}

output "ingress_class" {
  description = "Ingress class name for ALB"
  value = "alb"
}
