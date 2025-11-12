output "namespace" {
  description = "Namespace where ESO is installed"
  value       = helm_release.external_secrets.namespace
}

output "release_name" {
  description = "Helm release name"
  value       = helm_release.external_secrets.name
}

output "service_account" {
  description = "ESO service account name"
  value       = "external-secrets"
}

output "crds_ready" {
  description = "Indicates CRDs are ready after wait"
  value       = time_sleep.wait_for_crds.id
}
