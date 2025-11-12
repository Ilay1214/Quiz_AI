clusterName: ${cluster_name}
region: ${region}
vpcId: ${vpc_id}

serviceAccount:
  create: true
  name: aws-load-balancer-controller
  annotations:
    eks.amazonaws.com/role-arn: ${alb_controller_irsa_role_arn}

replicaCount: ${replica_count}

resources:
  requests:
    cpu: ${cpu_request}
    memory: ${memory_request}

# Enable subnet auto-discovery via tags
enableShield: false
enableWaf: false
enableWafv2: false
defaultTargetType: ip
createIngressClassResource: true
ingressClass: alb

# Enable webhook
webhookPort: 9443
webhook:
  failurePolicy: Ignore  # Don't fail if webhook is not ready

# Monitoring
metrics:
  enabled: true
