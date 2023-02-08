variable "cloud_tags" {
  description = "additional tags as a map"
  type        = map(string)
  default     = {}
}

variable "aws_default_region" {
  default = "us-east-1"
}

variable "vpc_name" {
  type        = string
  description = "vpc name"
}
