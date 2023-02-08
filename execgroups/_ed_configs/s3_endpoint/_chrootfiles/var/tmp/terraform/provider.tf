provider "aws" {
  region  = var.aws_default_region
}

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "~> 2.57.0"
    }
  }
}
