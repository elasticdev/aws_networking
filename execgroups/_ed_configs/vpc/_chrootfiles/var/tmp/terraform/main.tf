# get all available AZs in our region
data "aws_availability_zones" "available_azs" {
  state = "available"
}

# reserve Elastic IP to be used in our NAT gateway
resource "aws_eip" "nat_gw_elastic_ip" {
  vpc = true

  tags = merge(
      var.nat_gw_tags,
      var.cloud_tags,
      {
        Name            = var.vpc_name
        iac_environment = var.environment
        environment     = var.environment
      },
    )
}

# create VPC using the official AWS module
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "2.78.0"

  name = var.vpc_name
  cidr = var.main_network_block
  azs  = data.aws_availability_zones.available_azs.names

  private_subnets = [
    # this loop will create a one-line list as ["10.0.0.0/20", "10.0.16.0/20", "10.0.32.0/20", ...]
    # with a length depending on how many Zones are available
    for zone_id in data.aws_availability_zones.available_azs.zone_ids :
    cidrsubnet(var.main_network_block, var.subnet_prefix_extension, tonumber(substr(zone_id, length(zone_id) - 1, 1)) - 1)
  ]

  public_subnets = [
    # this loop will create a one-line list as ["10.0.128.0/20", "10.0.144.0/20", "10.0.160.0/20", ...]
    # with a length depending on how many Zones are available
    # there is a zone Offset variable, to make sure no collisions are present with private subnet blocks
    for zone_id in data.aws_availability_zones.available_azs.zone_ids :
    cidrsubnet(var.main_network_block, var.subnet_prefix_extension, tonumber(substr(zone_id, length(zone_id) - 1, 1)) + var.zone_offset - 1)
  ]

  # reference: https://registry.terraform.io/modules/terraform-aws-modules/vpc/aws/2.44.0#nat-gateway-scenarios
  enable_nat_gateway     = var.enable_nat_gateway
  single_nat_gateway     = var.single_nat_gateway
  one_nat_gateway_per_az = var.one_nat_gateway_per_az
  enable_dns_hostnames   = var.enable_dns_hostnames
  reuse_nat_ips          = var.reuse_nat_ips
  external_nat_ip_ids    = [aws_eip.nat_gw_elastic_ip.id]

  # add VPC/Subnet tags required by EKS (eks)
  tags = merge(
      var.vpc_tags,
      var.cloud_tags,
      {
        Name            = var.vpc_name
        iac_environment = var.environment
        environment     = var.environment
      },
    )

  public_subnet_tags = merge(
      var.vpc_tags,
      var.cloud_tags,
      var.public_subnet_tags,
      {
        Name                        = var.vpc_name
        iac_environment             = var.environment
        environment                 = var.environment
        subnet_environment          = "public"
      },
    )

  private_subnet_tags = merge(
      var.vpc_tags,
      var.cloud_tags,
      var.private_subnet_tags,
      {
        Name                                 = var.vpc_name
        iac_environment                      = var.environment
        environment                          = var.environment
        subnet_environment                   = "private"
      },
    )
}
