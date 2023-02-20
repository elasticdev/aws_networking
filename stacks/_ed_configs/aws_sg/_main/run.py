import json

class EdResourceSettings(object):

    def __init__(self,**kwargs):

        self.stack = kwargs["stack"]

    def _get_resource_values_to_add(self):
    
        self.resource_values = { "aws_default_region":self.stack.aws_default_region,
                                 "name":self.stack.tf_main_name,
                                 "tf_main_name":self.stack.tf_main_name,
                                 "region":self.stack.aws_default_region,
                                 "vpc_name":self.stack.vpc_name,
                                 "vpc":self.stack.vpc_name,
                                 "vpc_id":self.stack.vpc_id,
                                 "_id":"{}-{}".format(self.stack.resource_type,
                                                      self.stack.get_hash([ self.stack.tf_main_name,
                                                                            self.stack.vpc_id ]))
                                 }
    
        return self.resource_values

    def _get_docker_settings(self):
    
        env_vars = { "method": "create",
                     "aws_default_region": self.stack.aws_default_region,
                     "stateful_id":self.stack.stateful_id,
                     "resource_tags": "{},{},{},{}".format(self.stack.resource_type, 
                                                           self.stack.vpc_name, 
                                                           self.stack.vpc_name, 
                                                           self.stack.aws_default_region),
                     "name": self.stack.vpc_name }
    
        # include env vars in the host machine and pass it to the 
        # docker running container
        include_env_vars_keys = [ "aws_access_key_id",
                                  "aws_secret_access_key" ]
    
        self.docker_settings = { "env_vars":env_vars,
                                 "include_env_vars_keys":include_env_vars_keys }

        return self.docker_settings
    
    def _get_tf_settings(self):
    
        _default_tags = { "vpc_name":self.stack.vpc_name,
                          "vpc_id":self.stack.vpc_id }

        tf_vars = { "vpc_name": self.stack.vpc_name,
                    "vpc_id":self.stack.vpc_id,
                    "aws_default_region": self.stack.aws_default_region }

        if self.stack.cloud_tags_hash:
            tf_vars["cloud_tags"] = json.dumps(dict(_default_tags,**(self.stack.b64_decode(self.stack.cloud_tags_hash))))

        self.tf_settings = { "tf_vars":tf_vars,
                             "terraform_type":self.stack.terraform_type,
                             "tfstate_raw": "True" }
    
        return self.tf_settings

    def get(self):

        ################################################
        # ElasticDev Resource Setting
        # to wrap all the variables
        # into a b64 string
        ################################################
        ed_resource_settings = { "tf_settings":self._get_tf_settings(),
                                 "docker_settings":self._get_docker_settings(),
                                 "resource_values":self._get_resource_values_to_add(),
                                 "resource_type":self.stack.resource_type,
                                 "provider":self.stack.provider
                                 }

        return self.stack.b64_encode(ed_resource_settings)

def run(stackargs):

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

    stack.set_variable("provider","aws")

    # get vpc_id
    _lookup = { "must_exists":True,
                "resource_type": "vpc",
                "provider": stack.provider,
                "vpc": stack.vpc_name,
                "name": stack.vpc_name,
                "region": stack.aws_default_region,
                "search_keys": "vpc" }

    vpc_id = list(stack.get_resource(**_lookup))[0]["vpc_id"]

    # set variables
    stack.set_variable("vpc_id",vpc_id)
    stack.set_variable("resource_type","security_group")
    stack.set_variable("tf_main_name","{}-security-group-tf".format(stack.vpc_name))
    stack.set_variable("terraform_type","aws_security_group")

    # set ed/tf resource settings
    _ed_resource_settings = EdResourceSettings(stack=stack)

    env_vars = { "STATEFUL_ID":stack.stateful_id,
                 "METHOD":"create" }

    env_vars["ed_resource_settings_hash".upper()] = _ed_resource_settings.get()
    env_vars["aws_default_region".upper()] = stack.aws_default_region
    env_vars["docker_exec_env".upper()] = stack.docker_exec_env
    env_vars["use_docker".upper()] = True
    env_vars["CLOBBER"] = True

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
