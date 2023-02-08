variable "vpc_id" {
  type        = string
  description = "vpc id"
}

variable "aws_default_region" {
    description = "EC2 Region for the VPC"
    default = "us-east-1"
}
