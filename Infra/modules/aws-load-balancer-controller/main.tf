# NGINX Ingress Controller (fronted by ALB)
resource "helm_release" "ingress_nginx" {
  count = (var.enable_k8s && var.enable_ingress_nginx) ? 1 : 0
  name = "ingress-nginx"
  repository = "https://kubernetes.github.io/ingress-nginx"
  chart = "ingress-nginx"
  namespace  = var.nginx_namespace
  create_namespace = true
  wait = true
  wait_for_jobs = true

  set = [
    {
      name  = "controller.service.type"
      value = "ClusterIP"
    }
  ]
}

# AWS Load Balancer Controller
resource "helm_release" "aws_load_balancer_controller" {
  count = (var.enable_k8s && var.enable_aws_load_balancer_controller) ? 1 : 0
  name = "aws-load-balancer-controller"
  repository = "https://aws.github.io/eks-charts"
  chart = "aws-load-balancer-controller"
  namespace = "kube-system"
  wait = true
  wait_for_jobs = true

  set = [
    {
      name  = "clusterName"
      value = var.cluster_name
    },
    {
      name  = "serviceAccount.create"
      value = "false"
    },
    {
      name  = "serviceAccount.name"
      value = "aws-load-balancer-controller"
    },
    {
      name  = "serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn"
      value = var.alb_controller_irsa_role_arn
    }
  ]
}

# IngressClass for ALB
resource "kubernetes_manifest" "alb_ingress_class" {
  count = (var.enable_k8s && var.enable_aws_load_balancer_controller && var.create_alb_ingress_class) ? 1 : 0
  manifest = {
    apiVersion = "networking.k8s.io/v1"
    kind = "IngressClass"
    metadata = {
      name = "alb"
    }
    spec = {
      controller = "ingress.k8s.aws/alb"
    }
  }
}

# Edge Ingress: ALB -> NGINX controller Service
resource "kubernetes_manifest" "edge_ingress_to_nginx" {
  count = (var.enable_k8s && var.enable_edge_alb_to_nginx) ? 1 : 0
  manifest = {
    apiVersion = "networking.k8s.io/v1"
    kind = "Ingress"
    metadata = {
      name = "alb-to-nginx"
      namespace = var.nginx_namespace
      annotations = merge({
        "alb.ingress.kubernetes.io/scheme" = "internet-facing",
        "alb.ingress.kubernetes.io/target-type" = "ip",
        "alb.ingress.kubernetes.io/listen-ports" = "[{\"HTTP\":80}]",
        "alb.ingress.kubernetes.io/healthcheck-path" = "/",
        "alb.ingress.kubernetes.io/healthcheck-success-codes" = "404"
      }, var.edge_ingress_annotations)
    }
    spec = {
      ingressClassName = "alb"
      rules = [{
        http = {
          paths = [{
            path     = "/"
            pathType = "Prefix"
            backend = {
              service = {
                name = var.nginx_service_name
                port = { number = 80 }
              }
            }
          }]
        }
      }]
    }
  }
  depends_on = [
    helm_release.ingress_nginx,
    helm_release.aws_load_balancer_controller,
    kubernetes_manifest.alb_ingress_class
  ]
}