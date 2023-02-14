variable "stage" {
	default = "v1"
}

variable "resource_name" {
	default = "codebuild"
}

variable "lambda_invoke_arn" {
}

variable "lambda_name" {
    default = "process-webhook"
}

variable "apigateway_name" {
    default = "api-test"
}

variable "aws_default_region" {
    default = "eu-west-1"
}

variable "cloud_tags" {
  description = "additional tags as a map"
  type        = map(string)
  default     = {}
}
