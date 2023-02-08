variable "vpc_id" {
  type        = string
  description = "vpc id"
}

variable "aws_default_region" {
  default = "us-east-1"
}

variable "cloud_tags" {
  description = "additional tags as a map"
  type        = map(string)
  default     = {}
}
