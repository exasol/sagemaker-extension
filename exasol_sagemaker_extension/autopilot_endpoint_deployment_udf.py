import os
from typing import Type
from exasol_sagemaker_extension.autopilot_utils.enpoint_deployment import \
    AutopilotEndpointDeployment


class AutopilotEndpointDeploymentUDF:
    def __init__(self, exa,
                 deployment_class: Type[AutopilotEndpointDeployment] =
                 AutopilotEndpointDeployment):
        self.exa = exa
        self.counter = 0
        self.deployment_class = deployment_class

    def run(self, ctx):
        job_name = ctx.job_name
        endpoint_name = ctx.endpoint_name
        instance_type = ctx.instance_type
        instance_count = ctx.instance_count
        aws_s3_connection = ctx.aws_s3_connection
        aws_region = ctx.aws_region  # TODO

        aws_s3_conn_obj = self.exa.get_connection(aws_s3_connection)
        os.environ["AWS_DEFAULT_REGION"] = aws_region
        os.environ["AWS_ACCESS_KEY_ID"] = aws_s3_conn_obj.user
        os.environ["AWS_SECRET_ACCESS_KEY"] = aws_s3_conn_obj.password

        deployment_class_obj = self.deployment_class(job_name=job_name)
        deployment_class_obj.deploy(
            endpoint_name=endpoint_name,
            instance_type=instance_type,
            instance_count=instance_count
        )

        endpoint_problem_type = deployment_class_obj.get_endpoint_problem_type()

        ctx.emit(endpoint_problem_type)
        self.counter += 1
