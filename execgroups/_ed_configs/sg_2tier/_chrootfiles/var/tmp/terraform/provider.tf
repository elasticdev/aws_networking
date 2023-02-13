provider "aws" {
  region  = var.aws_default_region
  default_tags {
    tags = merge(
      var.cloud_tags,
      {
        orchestrated_by = "elasticdev"
      },
    )
  }
}
