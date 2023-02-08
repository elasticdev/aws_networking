def run(stackargs):

    import json

    # instantiate authoring stack
    stack = newStack(stackargs)

    # Add default variables
    stack.parse.add_required(key="vpc_name")
    stack.parse.add_required(key="stateful_id",default="_random")

    stack.parse.add_optional(key="environment",default="dev")
    stack.parse.add_optional(key="main_network_block",default="10.9.0.0/16")
    stack.parse.add_optional(key="enable_nat_gateway",default="true")
    stack.parse.add_optional(key="single_nat_gateway",default="true")
    stack.parse.add_optional(key="enable_dns_hostnames",default="true")
    stack.parse.add_optional(key="reuse_nat_ips",default="true")
    stack.parse.add_optional(key="one_nat_gateway_per_az",default="false")
    stack.parse.add_optional(key="publish_to_saas",default="null")

    # if eks_cluster is specified, then add the correct tags to the vpc 
    stack.parse.add_optional(key="eks_cluster",default="null")
    stack.parse.add_optional(key="labels",default="null")
    stack.parse.add_optional(key="tags",default="null")

    # docker image to execute terraform with
    stack.parse.add_optional(key="docker_exec_env",default="elasticdev/terraform-run-env")
    stack.parse.add_optional(key="aws_default_region",default="us-east-1")

    # Add execgroup
    stack.add_execgroup("elasticdev:::aws_networking::vpc")

    # Add substack
    stack.add_substack('elasticdev:::parse_terraform')
    stack.add_substack('elasticdev:::publish_vpc_info',"publish_vpc")

    # Initialize 
    stack.init_variables()
    stack.init_execgroups()
    stack.init_substacks()

    # set variables
    stack.set_variable("resource_type","vpc")
    _default_tags = {"vpc_name":stack.vpc_name}

    # if eks_cluster is provided, we modify the configs for eks
    stack.set_variable("vpc_tags",_default_tags.copy())
    stack.set_variable("nat_gw_tags",_default_tags.copy())
    stack.set_variable("public_subnet_tags",_default_tags.copy())
    stack.set_variable("private_subnet_tags",_default_tags.copy())

    if stack.eks_cluster: 
        stack.vpc_tags["kubernetes.io/cluster/{}".format(stack.eks_cluster)] = "shared"
        stack.public_subnet_tags["kubernetes.io/role/elb"] = "1"
        stack.private_subnet_tags["kubernetes.io/role/internal_elb"] = "1"
        stack.nat_gw_tags["Name"] = "{}-nat-eip".format(stack.eks_cluster)

    # Execute execgroup
    env_vars = {"TF_VAR_vpc_name":stack.vpc_name}
    env_vars["TF_VAR_environment"] = stack.environment
    env_vars["TF_VAR_main_network_block"] = stack.main_network_block
    env_vars["TF_VAR_vpc_tags"] = json.dumps(stack.vpc_tags)
    env_vars["TF_VAR_nat_gw_tags"] = json.dumps(stack.nat_gw_tags)
    env_vars["TF_VAR_public_subnet_tags"] = json.dumps(stack.public_subnet_tags)
    env_vars["TF_VAR_private_subnet_tags"] = json.dumps(stack.private_subnet_tags)

    env_vars["TF_VAR_enable_nat_gateway"] = "true"
    if stack.enable_nat_gateway in ["None",False,"false"]:
        env_vars["TF_VAR_enable_nat_gateway"] = "false"

    env_vars["TF_VAR_single_nat_gateway"] = "true"
    if stack.single_nat_gateway in ["None",False,"false"]:
        env_vars["TF_VAR_single_nat_gateway"] = "false"

    env_vars["TF_VAR_enable_dns_hostnames"] = "true"
    if stack.enable_dns_hostnames in ["None",False,"false"]:
        env_vars["TF_VAR_enable_dns_hostnames"] = "false"

    env_vars["TF_VAR_reuse_nat_ips"] = "true"
    if stack.reuse_nat_ips in ["None",False,"false"]:
        env_vars["TF_VAR_reuse_nat_ips"] = "false"

    env_vars["TF_VAR_one_nat_gateway_per_az"] = "false"
    if stack.one_nat_gateway_per_az in ["True",True,"true"]:
        env_vars["TF_VAR_one_nat_gateway_per_az"] = "true"

    #env_vars["TF_TEMPLATE_VARS"] = ",".join(env_vars.keys())

    env_vars["stateful_id".upper()] = stack.stateful_id
    env_vars["resource_type".upper()] = stack.resource_type
    env_vars["docker_exec_env".upper()] = stack.docker_exec_env
    env_vars["aws_default_region".upper()] = stack.aws_default_region
    env_vars["METHOD"] = "create"
    env_vars["CLOBBER"] = True
    env_vars["name".upper()] = stack.vpc_name
    env_vars["use_docker".upper()] = True
    #if stack.use_docker: env_vars["use_docker".upper()] = True

    # Set terraform environmental variables
    env_vars["TF_VAR_vpc_name"] = stack.vpc_name
    env_vars["TF_VAR_aws_default_region"] = stack.aws_default_region

    env_vars["RESOURCE_TAGS"] = "{},{},{}".format(stack.resource_type, stack.vpc_name, stack.aws_default_region)

    docker_env_fields_keys = env_vars.keys()
    docker_env_fields_keys.append("AWS_ACCESS_KEY_ID")
    docker_env_fields_keys.append("AWS_SECRET_ACCESS_KEY")
    docker_env_fields_keys.remove("METHOD")

    env_vars["DOCKER_ENV_FIELDS"] = ",".join(docker_env_fields_keys)

    inputargs = {"display":True}
    inputargs["env_vars"] = json.dumps(env_vars)
    inputargs["name"] = stack.vpc_name
    inputargs["stateful_id"] = stack.stateful_id
    if stack.labels: inputargs["labels"] = stack.labels
    if stack.tags: inputargs["tags"] = stack.tags
    stack.vpc.insert(**inputargs)

    # parse terraform and insert subnets 
    default_values = {"src_resource_type":"vpc"}
    default_values["src_resource_name"] = stack.vpc_name
    default_values["dst_resource_type"] = "subnet"
    default_values["vpc"] = stack.vpc_name
    default_values["must_exists"] = True
    default_values["aws_default_region"] = stack.aws_default_region
    default_values["provider"] = "aws"
    default_values["terraform_type"] = "aws_subnet"
    default_values["terraform_mode"] = "managed"
    default_values["mapping"] = json.dumps({"id":"subnet_id"})
    default_values["add_values"] = json.dumps({"vpc":stack.vpc_name})

    if stack.labels: default_values["labels"] = stack.labels
    if stack.tags: default_values["tags"] = stack.tags

    inputargs = {"default_values":default_values}
    inputargs["automation_phase"] = "infrastructure"
    inputargs["human_description"] ="Parse Terraform for subnets" 
    inputargs["display"] = True
    inputargs["display_hash"] = stack.get_hash_object(inputargs)
    stack.parse_terraform.insert(**inputargs)
    
    if not stack.publish_to_saas: return stack.get_results()

    # publish info on dashboard
    default_values = {"vpc_name":stack.vpc_name}
    inputargs = {"default_values":default_values}
    inputargs["automation_phase"] = "infrastructure"
    inputargs["human_description"] = 'Publish VPC {}'.format(stack.vpc_name)
    stack.publish_vpc.insert(display=True,**inputargs)

    return stack.get_results()
