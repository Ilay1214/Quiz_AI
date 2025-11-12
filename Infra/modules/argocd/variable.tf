variable "environment" {
  type    = string
  default = "prod"
}

variable "enable_apps" {
  type    = bool
  default = false
}

variable "app_manifest_path" {
  type    = string
  default = ""
}

variable "app_manifest_paths" {
  type    = list(string)
  default = []
}
