provider "aws" {
  region  = var.aws_default_region
  default_tags {
    tags = {
      Managed_by = 'elasticdev'
      }
  }
}

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "~> 2.57.0"
    }
  }
}
