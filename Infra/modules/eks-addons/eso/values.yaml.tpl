installCRDs: true
serviceAccount:
  create: true
  name: external-secrets
  annotations:
    eks.amazonaws.com/role-arn: ${eso_irsa_role_arn}

replicaCount: ${replica_count}

resources:
  requests:
    cpu: ${cpu_request}
    memory: ${memory_request}
  limits:
    cpu: ${cpu_limit}
    memory: ${memory_limit}

webhook:
  port: 9443

certController:
  requeueInterval: 5m

metrics:
  service:
    enabled: true
