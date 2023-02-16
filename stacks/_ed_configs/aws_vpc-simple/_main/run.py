import json

class EdResourceSettings(object):

    def __init__(self,stack):

        self.stack = stack

    def _get_resource_values_to_add(self):
    
        self.resource_values = { "aws_default_region":self.stack.aws_default_region,
                                 "region":self.stack.aws_default_region }
    
    def _get_docker_settings(self):
    
        ################################################
        # Docker vars and execution settings
        # will automatically be upper case
        ################################################
    
        env_vars = { "method": "create",
                     "aws_default_region": self.stack.aws_default_region,
                     "stateful_id":self.stack.stateful_id,
                     "resource_tags": "{},{},{}".format(self.stack.resource_type, 
                                                        self.stack.vpc_name, 
                                                        self.stack.aws_default_region),
                     "name": self.stack.vpc_name }
    
        # include env vars in the host machine and pass it to the 
        # docker running container
        include_env_vars_keys = [ "aws_access_key_id",
                                  "aws_secret_access_key" ]
    
        self.docker_settings = { "env_vars":env_vars,
                                 "include_env_vars_keys":include_env_vars_keys }
    
    def _get_tf_settings(self):
    
        ################################################
        # Terraform vars and execution settings
        # will automatically at TF_VAR_ as a prefix
        ################################################
        tf_vars = { "vpc_name": self.stack.vpc_name,
                    "vpc_tags": json.dumps(self.stack.vpc_tags),
                    "aws_default_region": self.stack.aws_default_region,
                    }
    
        self.tf_settings = { "tf_vars":tf_vars,
                             "terraform_type":"aws_vpc",
                             "tfstate_raw": "True",
                             "resource_keys": "all" }
    
    def get(self):

        # testtest777 labels additions
        resource_labels = { "keyboard":"querty",
                            "vendor":"compaq" }
    
        ################################################
        # ElasticDev Resource Setting
        # to wrap all the variables
        # into a b64 string
        ################################################
        ed_resource_settings = { "tf_settings":self._get_tf_settings(),
                                 "docker_settings":self._get_docker_settings(),
                                 "resource_values":self._get_resource_values_to_add(),
                                 "resource_labels":resource_labels,
                                 "resource_type":self.stack.resource_type,
                                 "provider":self.stack.provider
                                 }

        return self.stack.b64_encode(ed_resource_settings)

def run(stackargs):

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

    ################################################
    # Env Variables at execgroup run time
    ################################################

    _ed_resource_settings = EdResourceSettings(stack)

    env_vars = { "STATEFUL_ID":stack.stateful_id,
                 "METHOD":"create" }

    env_vars["ed_resource_settings_hash".upper()] = _ed_resource_settings.get()
    env_vars["aws_default_region".upper()] = stack.aws_default_region
    env_vars["docker_exec_env".upper()] = stack.docker_exec_env
    env_vars["use_docker".upper()] = True
    env_vars["CLOBBER"] = True

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
    #default_values = { "vpc_name":stack.vpc_name,
    #                   "cloud_tags_hash":stack.cloud_tags_hash,
    #                   "aws_default_region":stack.aws_default_region }

    #if hasattr(stack,"tier_level"): 
    #    default_values["tier_level"] = stack.tier_level

    #inputargs = {"default_values":default_values}
    #inputargs["automation_phase"] = "infrastructure"
    #inputargs["human_description"] = 'Creating security groups for VPC {}'.format(stack.vpc_name)
    #stack.aws_sg.insert(display=True,**inputargs)

    #if not stack.publish_to_saas: 
    #    return stack.get_results()

    ## publish info on dashboard
    #default_values = {"vpc_name":stack.vpc_name}
    #inputargs = {"default_values":default_values}
    #inputargs["automation_phase"] = "infrastructure"
    #inputargs["human_description"] = 'Publish VPC {}'.format(stack.vpc_name)
    #stack.publish_vpc.insert(display=True,**inputargs)

    return stack.get_results()
