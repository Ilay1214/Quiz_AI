locals {
  manifests = length(var.app_manifest_paths) > 0 ? var.app_manifest_paths : (
    var.app_manifest_path != "" ? [var.app_manifest_path] : []
  )
}

resource "helm_release" "argocd" {
  name = "argocd"
  repository = "https://argoproj.github.io/argo-helm"
  chart = "argo-cd"
  namespace = "argocd"
  version = "5.31.0"
  create_namespace = true

  set = [
    { 
      name = "server.replicas"
      value = "1" 
      },
    { 
      name = "controller.replicas"
      value = "1" 
      },
    { 
      name = "repoServer.replicas"
      value = "1" 
      },
    { 
      name = "redis.resources.requests.memory"
      value = "64Mi" 
      },
    { 
      name = "redis.resources.requests.cpu"
      value = "50m" 
      },
    { 
      name = "dex.enabled"
      value = "false" 
      },
    { 
      name = "notifications.enabled"
      value = "false" 
      },
    { 
      name = "applicationSet.enabled"
      value = "false" 
      }
  ]
}


resource "kubernetes_manifest" "app" {
  for_each = var.enable_apps ? toset(local.manifests) : toset([])
  manifest = yamldecode(file(each.value))
  depends_on = [helm_release.argocd]
}