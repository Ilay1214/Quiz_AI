output "cluster_endpoint" {
    value = module.eks.cluster_endpoint
}

output "cluster_certificate_authority_data" {
    value = module.eks.cluster_certificate_authority_data
}

output "cluster_name" {
    value = module.eks.cluster_name
}
output "cluster_auth_token" {
    value = data.aws_eks_cluster_auth.this.token
    sensitive = true
}

output "eso_irsa_role_arn" { value = module.eso_irsa_role.iam_role_arn }

output "cluster_oidc_issuer_url" { value = module.eks.cluster_oidc_issuer_url }

output "oidc_provider_arn" { value = module.eks.oidc_provider_arn }

output "cluster_autoscaler_irsa_role_arn" { value = module.cluster_autoscaler_irsa.iam_role_arn }

output "alb_controller_irsa_role_arn" {
  value = module.alb_controller_irsa.iam_role_arn
}