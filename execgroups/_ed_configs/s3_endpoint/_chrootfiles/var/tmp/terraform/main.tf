resource "aws_vpc_endpoint" "s3" {
  vpc_id      = var.vpc_id
  service_name = "com.amazonaws.${var.aws_default_region}.s3"

  tags = merge(
    var.cloud_tags,
    {
      Product = "vpc_endpoint"
    },
  )

}
