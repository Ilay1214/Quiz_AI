output "repository_names" {
  value = { for k, m in module.ecr : k => m.repository_name }
}
output "repository_urls" {
  value = { for k, m in module.ecr : k => m.repository_url }
}
output "repository_arns" {
  value = { for k, m in module.ecr : k => m.repository_arn }
}