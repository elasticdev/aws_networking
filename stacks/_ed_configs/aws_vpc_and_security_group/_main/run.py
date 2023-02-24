def run(stackargs):

    # instantiate authoring stack
    stack = newStack(stackargs)

    # Add default variables
    stack.parse.add_required(key="vpc_name")

    stack.parse.add_optional(key="tier_level")
    stack.parse.add_optional(key="vpc_tags")
    stack.parse.add_optional(key="nat_gw_tags")
    stack.parse.add_optional(key="public_subnet_tags")
    stack.parse.add_optional(key="private_subnet_tags")
    stack.parse.add_optional(key="enable_nat_gateway")
    stack.parse.add_optional(key="single_nat_gateway")
    stack.parse.add_optional(key="enable_dns_hostnames")
    stack.parse.add_optional(key="reuse_nat_ips")
    stack.parse.add_optional(key="one_nat_gateway_per_az")

    stack.parse.add_optional(key="aws_default_region",default="us-east-1")
    stack.parse.add_optional(key="environment",default="dev")
    stack.parse.add_optional(key="main_network_block",default="10.9.0.0/16")
    stack.parse.add_optional(key="labels",default="null")
    stack.parse.add_optional(key="tags",default="null")
    stack.parse.add_optional(key="publish_to_saas",default="null")

    # add substacks
    stack.add_substack('elasticdev:::aws_vpc')
    stack.add_substack('elasticdev:::aws_sg')
    stack.add_substack('elasticdev:::publish_vpc_info')

    # init the stack namespace
    stack.init_variables()
    stack.init_substacks()

    _default_tags = {"vpc_name":stack.vpc_name}
    stack.set_variable("public_subnet_tags",_default_tags.copy())
    stack.set_variable("private_subnet_tags",_default_tags.copy())

    # Create VPC
    default_values = {"vpc_name":stack.vpc_name}

    if hasattr(stack,"environment"): 
        default_values["environment"] = stack.environment

    if hasattr(stack,"main_network_block"): 
        default_values["main_network_block"] = stack.main_network_block

    if hasattr(stack,"vpc_tags"): 
        default_values["vpc_tags"] = stack.vpc_tags

    if hasattr(stack,"nat_gw_tags"): 
        default_values["nat_gw_tags"] = stack.nat_gw_tags

    if hasattr(stack,"public_subnet_tags"): 
        default_values["public_subnet_tags"] = stack.public_subnet_tags

    if hasattr(stack,"private_subnet_tags"): 
        default_values["private_subnet_tags"] = stack.private_subnet_tags

    if hasattr(stack,"enable_nat_gateway"): 
        default_values["enable_nat_gateway"] = stack.enable_nat_gateway

    if hasattr(stack,"single_nat_gateway"): 
        default_values["single_nat_gateway"] = stack.single_nat_gateway

    if hasattr(stack,"enable_dns_hostnames"): 
        default_values["enable_dns_hostnames"] = stack.enable_dns_hostnames

    if hasattr(stack,"reuse_nat_ips"): 
        default_values["reuse_nat_ips"] = stack.reuse_nat_ips

    if hasattr(stack,"one_nat_gateway_per_az"): 
        default_values["one_nat_gateway_per_az"] = stack.one_nat_gateway_per_az

    if hasattr(stack,"aws_default_region"): 
        default_values["aws_default_region"] = stack.aws_default_region

    if stack.labels: 
        default_values["labels"] = stack.labels

    if stack.tags: 
        default_values["tags"] = stack.tags

    if stack.publish_to_saas: 
        default_values["publish_to_saas"] = stack.publish_to_saas

    inputargs = {"default_values":default_values}
    inputargs["automation_phase"] = "infrastructure"
    inputargs["human_description"] = 'Creating VPC {}'.format(stack.vpc_name)
    stack.aws_vpc.insert(display=True,**inputargs)

    # Add security groups
    default_values = {"vpc_name":stack.vpc_name}

    if hasattr(stack,"tier_level"): 
        default_values["tier_level"] = stack.tier_level

    if hasattr(stack,"aws_default_region"): 
        default_values["aws_default_region"] = stack.aws_default_region

    if stack.labels: 
        default_values["labels"] = stack.labels

    if stack.tags: 
        default_values["tags"] = stack.tags

    inputargs = {"default_values":default_values}
    inputargs["automation_phase"] = "infrastructure"
    inputargs["human_description"] = 'Creating security groups for VPC {}'.format(stack.vpc_name)
    stack.aws_sg.insert(display=True,**inputargs)

    return stack.get_results()
