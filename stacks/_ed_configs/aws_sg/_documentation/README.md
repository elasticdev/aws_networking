**Description**
  - The stack attempts to create security group on an existing VPC

```
tier_level: 
    - 2 
        database
        web
    - 3
        database
        api
        web
```

**Required**

| argument      | description                            | var type | default      |
| ------------- | -------------------------------------- | -------- | ------------ |
| vpc_name   | name of the vpc                 | string   | None         |


**Optional**

| argument           | description                            | var type |  default      |
| aws_default_region   | default aws region               | string   | us-east-1         |
| tier_level   | the tier_level                | choice 2/3   | None |
| cloud_tags_hash | the tags for the resources in the cloud as base64 | string  | None         |
