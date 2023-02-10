provider "aws" {
  region  = var.aws_default_region

  default_tags {
    tags = merge(
      var.cloud_tags,
      {
        Orchestrated_by = 'elasticdev'
      },
    )
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
