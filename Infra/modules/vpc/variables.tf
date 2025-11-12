variable "vpc_cidr"   { type = string }
variable "num_of_azs" { type = number }
variable "environment" { type = string }
variable "project_name" { type = string }
variable "common_tags" { type = map(string) }
variable "cluster_name" { type = string }