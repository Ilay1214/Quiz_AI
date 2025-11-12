module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "${var.project_name}-${var.environment}-vpc"
  cidr = var.vpc_cidr

  azs = slice(data.aws_availability_zones.azs.names, 0, var.num_of_azs)
  private_subnets = [for i in range(var.num_of_azs) : cidrsubnet(var.vpc_cidr, 6, i)]
  public_subnets = [for i in range(var.num_of_azs) : cidrsubnet(var.vpc_cidr, 6, 5 + i)]
  intra_subnets = [for i in range(var.num_of_azs) : cidrsubnet(var.vpc_cidr, 6, 10 + i)]

  enable_nat_gateway = true
  enable_vpn_gateway = false
  single_nat_gateway = var.environment == "prod" ? false : true



  public_subnet_tags = {
    "kubernetes.io/role/elb" = "1"
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
  }


  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = "1"
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
  }

  tags = merge(var.common_tags, {
    Terraform = "true"
    Environment = var.environment
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
  })
}
