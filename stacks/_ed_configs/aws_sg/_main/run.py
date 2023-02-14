def run(stackargs):

    import json

    # instantiate authoring stack
    stack = newStack(stackargs)

    # Add default variables
    stack.parse.add_required(key="vpc_name")
    stack.parse.add_required(key="tier_level",default="null")
    stack.parse.add_required(key="stateful_id",default="_random")

    # docker image to execute terraform with
    stack.parse.add_optional(key="docker_exec_env",default="elasticdev/terraform-run-env:14")  # testtest 777 upgrade
    stack.parse.add_optional(key="aws_default_region",default="us-east-1")
    stack.parse.add_optional(key="use_docker",default=True,null_allowed=True)

    # labels and tags
    stack.parse.add_optional(key="labels",default="null")
    stack.parse.add_optional(key="tags",default="null")

    stack.parse.add_optional(key="cloud_tags_hash",default='null')

    # Add execgroup
    stack.add_execgroup("elasticdev:::aws_networking::sg_2tier")
    stack.add_execgroup("elasticdev:::aws_networking::sg_3tier")

    # Add substack
    stack.add_substack('elasticdev:::parse_terraform')

    # Initialize 
    stack.init_variables()
    stack.init_execgroups()
    stack.init_substacks()

    _lookup = {"must_exists":True}
    _lookup["resource_type"] = "vpc"
    _lookup["provider"] = "aws"
    _lookup["vpc"] = stack.vpc_name
    _lookup["name"] = stack.vpc_name
    _lookup["region"] = stack.aws_default_region
    _lookup["search_keys"] = "vpc"
    vpc_id = list(stack.get_resource(**_lookup))[0]["vpc_id"]

    # set variables
    stack.set_variable("vpc_id",vpc_id)
    stack.set_variable("resource_type","security_group")
    stack.set_variable("tf_main_name","{}-security-group-tf".format(stack.vpc_name))
    stack.set_variable("terraform_type","aws_security_group")

    # Execute execgroup
    # Set terraform environmental variables: TF_VAR*
    # TF_VAR is optional prefix
    tf_exec_env_vars = { "vpc_name": stack.vpc_name,
                         "vpc_id":stack.vpc_id,
                         "aws_default_region": stack.aws_default_region }

    ed_tf_settings = { "tf_exec_env_vars":tf_exec_env_vars,
                       "terraform_type":stack.terraform_type,
                       "tf_exec_include_raw": "True" }

    _default_tags = { "vpc_name":stack.vpc_name,
                      "vpc_id":stack.vpc_id }

    ed_resource_settings = { "resource_type":stack.resource_type,
                             "provider":"aws" }

    ed_resource_settings["resource_values_hash"] = stack.b64_encode({ "aws_default_region":stack.aws_default_region,
                                                                      "name":stack.tf_main_name,
                                                                      "tf_main_name":stack.tf_main_name,
                                                                      "region":stack.aws_default_region })

    if stack.cloud_tags_hash: 
        tf_exec_env_vars["cloud_tags"] = json.dumps(stack.b64_decode(stack.cloud_tags_hash))
        #tf_exec_env_vars["cloud_tags"] = json.dumps(dict(_default_tags,**(stack.b64_decode(stack.cloud_tags_hash))))

    env_vars = { "METHOD":"create" }
    env_vars["ed_resource_settings_hash".upper()] = stack.b64_encode(ed_resource_settings)
    env_vars["ed_tf_settings_hash".upper()] = stack.b64_encode(ed_tf_settings)

    env_vars["aws_default_region".upper()] = stack.aws_default_region
    env_vars["stateful_id".upper()] = stack.stateful_id
    env_vars["resource_type".upper()] = stack.resource_type  # testtest777 remove this
    env_vars["docker_exec_env".upper()] = stack.docker_exec_env

    env_vars["use_docker".upper()] = True
    env_vars["CLOBBER"] = True

    env_vars["RESOURCE_TAGS"] = "{},{},{},{}".format(stack.resource_type, 
                                                     stack.vpc_id, 
                                                     stack.vpc_name, 
                                                     stack.aws_default_region)

    docker_env_fields_keys = env_vars.keys()
    docker_env_fields_keys.append("AWS_ACCESS_KEY_ID")
    docker_env_fields_keys.append("AWS_SECRET_ACCESS_KEY")
    docker_env_fields_keys.remove("METHOD")

    env_vars["DOCKER_ENV_FIELDS"] = ",".join(docker_env_fields_keys)

    inputargs = {"display":True}
    inputargs["env_vars"] = json.dumps(env_vars)
    inputargs["display"] = True
    inputargs["name"] = stack.vpc_name
    inputargs["stateful_id"] = stack.stateful_id
    inputargs["human_description"] = "Creating security groups for vpc {}".format(stack.vpc_name)

    if stack.labels: 
        inputargs["labels"] = stack.labels

    if stack.tags: 
        inputargs["tags"] = stack.tags

    if stack.tier_level == "2":
        stack.sg_2tier.insert(**inputargs)
    else:
        stack.sg_3tier.insert(**inputargs)

    # revisit 
    # testtest777
    # parse terraform and insert security groups 
    #default_values = {"src_resource_type":"security_group"}
    #default_values["src_resource_name"] = stack.tf_main_name
    #default_values["dst_resource_type"] = "security_group"
    #default_values["vpc"] = stack.vpc_name
    #default_values["must_exists"] = True
    #default_values["aws_default_region"] = stack.aws_default_region
    #default_values["provider"] = "aws"
    #default_values["terraform_type"] = stack.terraform_type,
    #default_values["terraform_mode"] = "managed"
    #default_values["mapping"] = json.dumps({"id":"sg_id"})
    #default_values["add_values"] = json.dumps({"vpc_id":stack.vpc_id,"vpc":stack.vpc_name})

    #if stack.labels: 
    #    default_values["labels"] = stack.labels

    #if stack.tags: 
    #    default_values["tags"] = stack.tags

    #inputargs = {"default_values":default_values}
    #inputargs["automation_phase"] = "infrastructure"
    #inputargs["human_description"] ="Parse Terraform for security groups" 
    #inputargs["display"] = True
    #inputargs["display_hash"] = stack.get_hash_object(inputargs)
    #stack.parse_terraform.insert(**inputargs)

    return stack.get_results()
