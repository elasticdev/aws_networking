variable "environment" {
  type        = string
  description = "Environment: dev, staging, prod, ..."
}

variable "aws_default_region" {
  default = "eu-west-1"
}

variable "vpc_name" {
  type        = string
  description = "vpc name"
}

variable "main_network_block" {
  type        = string
  description = "Base CIDR block to be used in our VPC."
}

variable "subnet_prefix_extension" {
  type        = number
  description = "CIDR block bits extension to calculate CIDR blocks of each subnetwork."
  default     = 4
}

variable "zone_offset" {
  type        = number
  description = "CIDR block bits extension offset to calculate Public subnets, avoiding collisions with Private subnets."
  default     = 8
}

variable "enable_nat_gateway" {
  default     = true
}

variable "single_nat_gateway" {
  default     = true
}

variable "enable_dns_hostnames" {
  default     = true
}

variable "reuse_nat_ips" {
  default     = true
}

# enable single NAT Gateway to save some money
# WARNING: this could create a single point of failure, since we are creating a NAT Gateway in one AZ only
variable "one_nat_gateway_per_az" {
  default     = false
}

variable "vpc_tags" {
  description = "VPC resource tags"
  type        = map(string)
}

variable "nat_gw_tags" {
  description = "NAT gw tags"
  type        = map(string)
}

variable "public_subnet_tags" {
  default     = {"kubernetes.io/role/elb":"1"}
  description = "public subnet tags"
  type        = map(string)
}

variable "private_subnet_tags" {
  default     = {"kubernetes.io/role/internal_elb":"1"}
  description = "private subnet tags"
  type        = map(string)
}

variable "cloud_tags" {
  description = "additional tags as a map"
  type        = map(string)
  default     = {}
}
