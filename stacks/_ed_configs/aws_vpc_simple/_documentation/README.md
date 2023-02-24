**Description**
  - This stack creates a simple VPC without a NAT (cheaper)

**Required**

| argument      | description                            | var type | default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| vpc_name   | name of the vpc                 | string   | None         |

**Optional**

| argument           | description                            | var type |  default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| environment   | the environment                | string   | dev |
| enable_dns_hostnames   | enable dns hostnames                | string   | |
| eks_cluster   | provide an EKS cluster if vpc requires eks settings                | string   | |
| labels   | the labels for the vpc.  this is typically needed for EKS                | string   | |
| tags   | the tags for the vpc.  this is typically needed for EKS                | string   | |
| aws_default_region   | default aws region               | string   | us-east-1         |
| docker_exec_env   | the docker container to execute the underlying Terraform templates               | string   | elasticdev/terraform-run-env         |
| cloud_tags_hash | the tags for the resources in the cloud as base64 | string  | None         |
