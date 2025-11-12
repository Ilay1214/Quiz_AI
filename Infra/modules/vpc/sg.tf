resource "aws_security_group" "karpenter_nodes" {
  name = "${var.project_name}-${var.environment}-karpenter-nodes-sg"
  vpc_id = module.vpc.vpc_id

  ingress {
    from_port = 0 
    to_port = 65535 
    protocol = "tcp"
    self = true
  }
  egress {
    from_port = 0 
    to_port = 0 
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "${var.project_name}-${var.environment}-karpenter-nodes-sg"
    "karpenter.sh/discovery" ="${var.environment}-eks-cluster"
    "kubernetes.io/cluster/${var.environment}-eks-cluster" = "owned"
  }
}

resource "aws_security_group" "alb" {
  name = "${var.project_name}-${var.environment}-alb-sg"
  vpc_id = module.vpc.vpc_id

  ingress { 
    from_port = 80
    to_port = 80  
    protocol = "tcp" 
    cidr_blocks = ["0.0.0.0/0"] 
  }
  ingress { 
    from_port = 443
    to_port = 443 
    protocol = "tcp" 
    cidr_blocks = ["0.0.0.0/0"] 
  }
  egress  { 
    from_port = 0
    to_port = 0   
    protocol = "-1"  
    cidr_blocks = ["0.0.0.0/0"] 
  }
}


resource "aws_security_group_rule" "nodes_ingress_from_alb_nodeport" {
  type = "ingress"
  security_group_id = aws_security_group.karpenter_nodes.id
  from_port = 30000
  to_port = 32767
  protocol = "tcp"
  source_security_group_id = aws_security_group.alb.id
  description = "ALB to NodePort on worker nodes"
}