resource "helm_release" "external_secrets" { 
  count = var.enable_k8s ? 1 : 0 
  name = "external-secrets" 
  repository = "https://charts.external-secrets.io" 
  chart = "external-secrets" 
  namespace = "external-secrets" 
  version = "0.10.4" 
  create_namespace = true 
  wait = true
  wait_for_jobs = true
  
  set =[{
    name  = "installCRDs"
    value = "true"
  },
  
{
    name  = "serviceAccount.create"
    value = "true"
  },
  
 {
    name  = "serviceAccount.name"
    value = "external-secrets"
  },
  
{
    name  = "serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn"
    value = var.irsa_role_arn
  }
  ]
}

# Wait for CRDs to be fully available 
resource "time_sleep" "wait_for_crds" {
  count = var.enable_k8s ? 1 : 0
  
  create_duration = "30s"
  
  depends_on = [helm_release.external_secrets]
}

