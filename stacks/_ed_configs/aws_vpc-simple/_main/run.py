def run(stackargs):

    import json

    # instantiate authoring stack
    stack = newStack(stackargs)

    # Add default variables
    stack.parse.add_required(key="vpc_name")
    stack.parse.add_required(key="stateful_id",default="_random")

    stack.parse.add_optional(key="tier_level")
    stack.parse.add_optional(key="aws_default_region",default="us-east-1")

    # docker image to execute terraform with
    stack.parse.add_optional(key="docker_exec_env",default="elasticdev/terraform-run-env:14")  # testtest 777 upgrade

    # if eks_cluster is specified, then add the correct tags to the vpc 
    stack.parse.add_optional(key="eks_cluster",default="null")

    stack.parse.add_optional(key="publish_to_saas",default="null")
    stack.parse.add_optional(key="cloud_tags_hash",default='null')

    # Add execgroup
    stack.add_execgroup("elasticdev:::aws_networking::vpc_simple")

    # Add substack
    stack.add_substack('elasticdev:::parse_terraform')
    stack.add_substack('elasticdev:::aws_sg')
    stack.add_substack('elasticdev:::publish_vpc_info',"publish_vpc")

    # Initialize 
    stack.init_variables()
    stack.init_execgroups()
    stack.init_substacks()

    # set variables
    stack.set_variable("resource_type","vpc")
    stack.set_variable("terraform_type","aws_vpc")
    stack.set_variable("provider","aws")

    _default_tags = {"vpc_name":stack.vpc_name}
    stack.set_variable("vpc_tags",_default_tags.copy())
    stack.set_variable("public_subnet_tags",_default_tags.copy())
    stack.set_variable("private_subnet_tags",_default_tags.copy())

    # if eks_cluster is provided, we modify the configs
    # if we are using a vpc without a nat, the eks must be in public network
    # the internal lb must also be in public
    if stack.eks_cluster: 
        stack.vpc_tags["kubernetes.io/cluster/{}".format(stack.eks_cluster)] = "shared"
        stack.public_subnet_tags["kubernetes.io/role/elb"] = "1"
        stack.public_subnet_tags["kubernetes.io/role/internal_elb"] = "1"
        #stack.private_subnet_tags["kubernetes.io/role/internal_elb"] = "1"

    # Set terraform environmental variables: TF_VAR*
    # TF_VAR is optional prefix
    tf_exec_env_vars = { "vpc_name": stack.vpc_name,
                         "vpc_tags": json.dumps(stack.vpc_tags),
                         "aws_default_region": stack.aws_default_region,
                         }

    ed_tf_settings = { "tf_exec_env_vars":tf_exec_env_vars,
                       "terraform_type":"aws_vpc",
                       "tf_exec_include_raw": "True",
                       "tf_exec_resource_keys": "all" }

    ed_resource_settings = { "resource_type":stack.resource_type,
                             "provider":stack.provider }

    ed_resource_settings["resource_values_hash"] = stack.b64_encode({ "aws_default_region":stack.aws_default_region,
                                                                      "region":stack.aws_default_region })

    # testtest777 labels additions
    ed_resource_settings["resource_labels_hash"] = stack.b64_encode({ "keyboard":"querty",
                                                                      "vendor":"compaq" })
    if stack.cloud_tags_hash: 
        tf_exec_env_vars["cloud_tags"] = json.dumps(stack.b64_decode(stack.cloud_tags_hash))

    env_vars = { "METHOD":"create" }
    env_vars["ed_resource_settings_hash".upper()] = stack.b64_encode(ed_resource_settings)
    env_vars["ed_tf_settings_hash".upper()] = stack.b64_encode(ed_tf_settings)

    # not necessary to set since it's set above in tf_exec_env_vars
    env_vars["aws_default_region".upper()] = stack.aws_default_region
    env_vars["stateful_id".upper()] = stack.stateful_id
    env_vars["resource_type".upper()] = stack.resource_type  # testtest777 remove this
    env_vars["docker_exec_env".upper()] = stack.docker_exec_env
    env_vars["name".upper()] = stack.vpc_name

    env_vars["use_docker".upper()] = True
    env_vars["CLOBBER"] = True

    env_vars["RESOURCE_TAGS"] = "{},{},{}".format(stack.resource_type, 
                                                  stack.vpc_name, 
                                                  stack.aws_default_region)

    # env_vars that will be passed to
    # the docker run environment as .env
    docker_env_fields_keys = env_vars.keys()
    docker_env_fields_keys.append("AWS_ACCESS_KEY_ID")
    docker_env_fields_keys.append("AWS_SECRET_ACCESS_KEY")
    docker_env_fields_keys.remove("METHOD")
    env_vars["DOCKER_ENV_FIELDS"] = ",".join(docker_env_fields_keys)

    inputargs = {"display":True}
    inputargs["env_vars"] = json.dumps(env_vars)
    inputargs["name"] = stack.vpc_name
    inputargs["stateful_id"] = stack.stateful_id
    stack.vpc_simple.insert(**inputargs)

    # testtest777
    # parse terraform and insert subnets 
    #overide_values = { "src_resource_type":stack.resource_type,
    #                   "src_provider":stack.provider,
    #                   "src_resource_name":stack.vpc_name,
    #                   "src_terraform_type":stack.terraform_type,
    #                   "src_terraform_mode":"managed"}

    #overide_values["dst_resource_type"] = "subnet"
    #overide_values["must_exists"] = True
    #overide_values["aws_default_region"] = stack.aws_default_region
    #overide_values["mapping"] = json.dumps({"id":"subnet_id"})
    #overide_values["add_values"] = json.dumps({"vpc":stack.vpc_name})

    #inputargs = {"overide_values":overide_values}
    #inputargs["automation_phase"] = "infrastructure"
    #inputargs["human_description"] ="Parse Terraform for subnets" 
    #inputargs["display"] = True
    #inputargs["display_hash"] = stack.get_hash_object(inputargs)
    #stack.parse_terraform.insert(**inputargs)

    # Add security groups
    default_values = { "vpc_name":stack.vpc_name,
                       "aws_default_region":stack.aws_default_region }

    if hasattr(stack,"tier_level"): 
        default_values["tier_level"] = stack.tier_level

    inputargs = {"default_values":default_values}
    inputargs["automation_phase"] = "infrastructure"
    inputargs["human_description"] = 'Creating security groups for VPC {}'.format(stack.vpc_name)
    stack.aws_sg.insert(display=True,**inputargs)

    if not stack.publish_to_saas: 
        return stack.get_results()

    # publish info on dashboard
    default_values = {"vpc_name":stack.vpc_name}
    inputargs = {"default_values":default_values}
    inputargs["automation_phase"] = "infrastructure"
    inputargs["human_description"] = 'Publish VPC {}'.format(stack.vpc_name)
    stack.publish_vpc.insert(display=True,**inputargs)

    return stack.get_results()
