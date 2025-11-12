module "ecr" {
  source  = "terraform-aws-modules/ecr/aws"
  version = "~> 2.0"
  
  for_each = toset(var.ecr_names) 


  repository_name = each.key

  repository_read_write_access_arns = [data.aws_caller_identity.current.arn]
  repository_lifecycle_policy = jsonencode({
    rules = [
      {
        rulePriority = 1,
        description  = "Keep last 30 images",
        selection = {
          tagStatus = "tagged",
          tagPrefixList = ["v"],
          countType  = "imageCountMoreThan",
          countNumber = 30
        },
        action = {
          type = "expire"
        }
      }
    ]
  })

  tags = {
    Terraform   = "true"
    Environment = "${var.environment}"
  }
}