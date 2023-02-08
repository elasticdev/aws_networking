**Description**
  - This stack creates a simple VPC

**Required**

| argument      | description                            | var type | default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| vpc_name   | name of the vpc                 | string   | None         |

**Optional**

| argument           | description                            | var type |  default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| environment   | the environment                | string   | dev |
| main_network_block   | the cidr for the main network nat                | string   | 10.9.0.0/16 |
| enable_nat_gateway   | enable nat gateway                | string   | |
| single_nat_gateway   | single nat gateway                | string   | |
| enable_dns_hostnames   | enable dns hostnames                | string   | |
| reuse_nat_ips   | reuse nat ips                | string   | |
| one_nat_gateway_per_az   | set true if you want one nat gateway per az (more expensive)                | string   | |
| eks_cluster   | provide an EKS cluster if vpc requires eks settings                | string   | |
| labels   | the labels for the vpc.  this is typically needed for EKS                | string   | |
| tags   | the tags for the vpc.  this is typically needed for EKS                | string   | |
| aws_default_region   | default aws region               | string   | us-east-1         |
| docker_exec_env   | the docker container to execute the underlying Terraform templates               | string   | elasticdev/terraform-run-env         |
