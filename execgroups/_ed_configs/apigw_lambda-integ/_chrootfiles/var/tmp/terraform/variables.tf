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
}

#variable "lambda_arn" {
#variable "lambda_arn" {
#    default = "arn:aws:lambda:eu-west-1:3452345432:function:process-webhook"
#}

