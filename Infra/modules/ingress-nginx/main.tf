resource "helm_release" "ingress_nginx" {
  name       = "ingress-nginx"
  repository = "https://kubernetes.github.io/ingress-nginx"
  chart      = "ingress-nginx"
  namespace  = var.namespace
  create_namespace = true
  version    = "4.8.3"
  wait       = true
  timeout    = 600

  set = [
    { name  = "controller.service.type",    value = "ClusterIP" },
    { name  = "controller.publishService.enabled", value = "true" },
    { name  = "controller.ingressClassResource.enabled", value = "true" },
    { name  = "controller.ingressClassResource.name",    value = "nginx" },
    { name  = "controller.ingressClassResource.controllerValue",
      value = "k8s.io/ingress-nginx" },
    { name  = "controller.ingressClassResource.default", value = "false" }
  ]
}