**Description**
  - The stack that creates a 3tier VPC with terraform templates
     - database

     - api -> database
        
     - web -> api
           <- http
           <- https
           <- ssh

     - bastion -> web,api,database
           <- ssh

**Required**

| argument      | description                            | var type | default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| vpc_name   | name of the vpc                 | string   | None         |

**Optional**

| argument           | description                            | var type |  default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| aws_default_region   | default aws region               | string   | us-east-1         |
| tier_level   | "2" or "3" tier for security groups                | string   |  |
| vpc_tags   | AWS tags for the vpc                | string   | |
| nat_gw_tags   | AWS tags for the nat gw                | string   | |
| public_subnet_tags   | AWS tags for the public subnet                | string   | |
| private_subnet_tags   | AWS tags for the private subnet                | string   | |
| enable_nat_gateway   | enable nat gateway                | string   | |
| single_nat_gateway   | single nat gateway                | string   | |
| enable_dns_hostnames   | enable dns hostnames                | string   | |
| reuse_nat_ips   | reuse nat ips                | string   | |
| one_nat_gateway_per_az   | set true if you want one nat gateway per az (more expensive)                | string   | |
| environment   | the environment                | string   | dev |
| main_network_block   | the cidr for the main network nat                | string   | 10.9.0.0/16 |
| labels   | ED resource labels for the vpc                 | string   | None |
| tags   | ED resource tags for the vpc                 | string   | None |

**Sample entry**

```
infrastructure:
   vpc:
       stack_name: elasticdev:::aws_vpc_and_security_group
       arguments:
          main_network_block: 10.13.0.0/16
          tier_level: "2"
          enable_nat_gateway: true
          single_nat_gateway: true
          enable_dns_hostnames: true
          reuse_nat_ips: true
          one_nat_gateway_per_az: false
       credentials:
           - reference: aws_2
             orchestration: true
```

**Misc Sample**
```
main_network_block: 10.7.0.0/16
vpc_tags: {"kubernetes.io/cluster/eks_dev":"shared"}
nat_gw_tags: {"Name":"eks_vpc-nat-eip"}
public_subnet_tags: {"kubernetes.io/role/elb":"1"}
private_subnet_tags: {"kubernetes.io/role/internal_elb":"1"}
enable_nat_gateway: true
single_nat_gateway: true
enable_dns_hostnames: true
reuse_nat_ips: true
one_nat_gateway_per_az: false
```
