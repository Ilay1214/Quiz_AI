locals {
  manifests = length(var.app_manifest_paths) > 0 ? var.app_manifest_paths : (
    var.app_manifest_path != "" ? [var.app_manifest_path] : []
  )
}

# Only create ArgoCD Application 
resource "kubernetes_manifest" "app" {
  for_each = toset(local.manifests)
  manifest = yamldecode(file(each.value))
}
