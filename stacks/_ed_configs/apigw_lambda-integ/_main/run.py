import json

# lookup lambda execution arn
def _set_lambda_arn(stack):
    
    _lookup = {"must_exists":True}
    _lookup["resource_type"] = "aws_lambda"
    _lookup["name"] = stack.lambda_name
    _lookup["region"] = stack.aws_default_region
    lambda_invoke_arn = list(stack.get_resource(**_lookup))[0]["invoke_arn"]

    stack.set_variable("lambda_invoke_arn",lambda_invoke_arn)

    return

class EdResourceSettings(object):

    def __init__(self,**kwargs):

        self.stack = kwargs["stack"]

    def _get_resource_values_to_add(self):
    
        self.resource_values = { "aws_default_region":self.stack.aws_default_region,
                                 "region":self.stack.aws_default_region }

        self.resource_values["name"] = self.stack.resource_name

        return self.resource_values

    def _get_docker_settings(self):
    
        env_vars = { "method": "create",
                     "stateful_id":self.stack.stateful_id,
                     "resource_tags": "{},{},{}".format(self.stack.resource_type, 
                                                        self.stack.resource_name,
                                                        self.stack.aws_default_region),
                     "aws_default_region": self.stack.aws_default_region,
                     "name": self.stack.resource_name }
    
        include_env_vars_keys = [ "aws_access_key_id",
                                  "aws_secret_access_key" ]
    
        self.docker_settings = { "env_vars":env_vars,
                                 "include_env_vars_keys":include_env_vars_keys }

        return self.docker_settings
    
    def _get_tf_settings(self):

        tf_vars = { "aws_default_region": self.stack.aws_default_region }
        tf_vars["apigateway_name"] = self.stack.apigateway_name
        tf_vars["lambda_name"] = self.stack.lambda_name
        tf_vars["resource_name"] = self.stack.resource_name
        tf_vars["aws_default_region"] = self.stack.aws_default_region
        tf_vars["stage"] = self.stack.stage
        tf_vars["lambda_invoke_arn"] = self.stack.lambda_invoke_arn

        if self.stack.cloud_tags_hash: 
            tf_vars["cloud_tags"] = json.dumps(self.stack.b64_decode(self.stack.cloud_tags_hash))

        add_keys = [ "name",
                     "arn",
                     "description",
                     "execution_arn",
                     "root_resource_id",
                     "id"]

        maps = { "gateway_id":"arn" }

        resource_params = { "add_keys": add_keys,
                            "map_keys": maps,
                            "include_raw": "True" }

        self.tf_settings = { "tf_vars":tf_vars,
                             "terraform_type":self.stack.terraform_type,
                             "resource_params": resource_params }

        return self.tf_settings

    def get(self):

        ed_resource_settings = { "tf_settings":self._get_tf_settings(),
                                 "docker_settings":self._get_docker_settings(),
                                 "resource_type":self.stack.resource_type,
                                 "resource_values":self._get_resource_values_to_add(),
                                 "provider":self.stack.provider
                                 }

        return self.stack.b64_encode(ed_resource_settings)

def run(stackargs):

    # instantiate authoring stack
    stack = newStack(stackargs)

    stack.parse.add_required(key="apigateway_name")
    stack.parse.add_required(key="lambda_name")

    stack.parse.add_optional(key="resource_name",default="codebuild")
    stack.parse.add_optional(key="aws_default_region",default="us-west-1")
    stack.parse.add_optional(key="stage",default="v1")

    stack.parse.add_optional(key="docker_exec_env",default="elasticdev/terraform-run-env:1.3.7")
    stack.parse.add_optional(key="cloud_tags_hash",default="null")
    stack.parse.add_optional(key="publish_to_saas",default="null")

    # Add execgroup
    stack.add_execgroup("elasticdev:::aws_networking::apigw_lambda-integ","cloud_resource")

    # Initialize 
    stack.init_variables()
    stack.init_execgroups()

    stack.set_variable("stateful_id",stack.random_id())
    stack.set_variable("resource_type","apigateway_restapi_lambda")
    stack.set_variable("provider","aws")

    stack.set_variable("resource_name",stack.apigateway_name)
    stack.set_variable("terraform_type","aws_api_gateway_rest_api")

    _set_lambda_arn(stack)

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
    inputargs["name"] = stack.resource_name
    inputargs["stateful_id"] = stack.stateful_id
    inputargs["human_description"] = 'Creates API Gateway "{}"'.format(stack.apigateway_name)
    inputargs["display_hash"] = stack.get_hash_object(inputargs)

    stack.cloud_resource.insert(**inputargs)

    if stack.publish_to_saas:

        keys_to_publish = [ "name",
                            "arn",
                            "execution_arn",
                            "root_resource_id",
                            "id"]

        default_values = { "resource_type":stack.resource_type }
        default_values["name"] = stack.hostname
        default_values["publish_keys_hash"] = stack.b64_encode(keys_to_publish)

        overide_values = { "prefix_key": "apigw" }

        inputargs = { "default_values":default_values,
                      "overide_values":overide_values }

        inputargs["automation_phase"] = "infrastructure"
        inputargs["human_description"] = 'Publish resource info for {}'.format(stack.resource_type)

        stack.publish_resource.insert(display=True,**inputargs)

    return stack.get_results()
