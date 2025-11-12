resource "kubernetes_manifest" "cluster_secret_store" { 
  count = (var.enable_k8s && var.create_cluster_secret_store && var.create_crd_resources) ? 1 : 0 
  manifest = { 
    apiVersion = "external-secrets.io/v1beta1" 
    kind = "ClusterSecretStore" 
    metadata = { name = var.secret_store_name } 
    spec = { 
      provider = { 
        aws = { 
          service = "SecretsManager" 
          region = var.region 
          auth = { 
            jwt = { 
              serviceAccountRef = { 
                name = var.sa_name 
                namespace = var.sa_namespace 
                } 
              } 
            } 
          } 
        } 
      } 
  } 
  depends_on = [ time_sleep.wait_for_crds ]
} 


resource "kubernetes_namespace_v1" "ns" { 
  for_each = (var.enable_k8s && var.manage_namespaces) ? var.namespaces : {} 
    metadata { name = each.value.name } 
} 


resource "kubernetes_manifest" "app_env" { 
  for_each = (var.enable_k8s && var.create_crd_resources) ? var.namespaces : {} 
  manifest = { 
    apiVersion = "external-secrets.io/v1beta1" 
    kind = "ExternalSecret" 
    metadata = { 
      name = "app-env" 
      namespace = each.value.name 
      } 
    spec = { 
      secretStoreRef = { 
      name = var.secret_store_name 
      kind = "ClusterSecretStore" } 
    refreshInterval = "1h" 
    target = { 
      name = "app-env" 
      creationPolicy = "Owner" 
      template = { type = "Opaque" } 
      } 
    dataFrom = [{ extract = { key = each.value.remote_key } }] 
      } 
      } 
    depends_on = [ 
      kubernetes_namespace_v1.ns, 
      kubernetes_manifest.cluster_secret_store, 
      time_sleep.wait_for_crds 
      ] 
} 
      
      
resource "kubernetes_manifest" "mysql_ca" { 
  for_each = (var.enable_k8s && var.create_crd_resources) ? var.namespaces : {} 
  manifest = { 
    apiVersion = "external-secrets.io/v1beta1" 
    kind = "ExternalSecret" 
    metadata = { 
      name = "mysql-ca" 
      namespace = each.value.name 
      } 
    spec = { 
      secretStoreRef = { 
        name = var.secret_store_name 
        kind = "ClusterSecretStore" 
        } 
      refreshInterval = "1h" 
      target = { 
        name = "mysql-ca" 
        creationPolicy = "Owner" 
        template = { type = "Opaque" } 
        } 
      data = [{ 
        secretKey = "ca.pem" 
        remoteRef = { 
          key = each.value.remote_key 
          property = var.mysql_ca_property 
          } 
        }] 
      } 
   } 
   depends_on = [ 
    kubernetes_namespace_v1.ns, 
    kubernetes_manifest.cluster_secret_store, 
    time_sleep.wait_for_crds 
    ] 
}