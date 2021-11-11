import os
from typing import Callable
from exasol_sagemaker_extension.autopilot_utils.enpoint_deployment import \
    AutopilotEndpointDeployment


class AutopilotEndpointDeploymentUDF:
    def __init__(self, exa,
                 deploy_method: Callable = AutopilotEndpointDeployment.deploy):
        self.exa = exa
        self.counter = 0
        self.deploy_method = deploy_method

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

        endpoint_name = self.deploy_method(
            job_name=job_name,
            endpoint_name=endpoint_name,
            instance_type=instance_type,
            instance_count=instance_count
        )

        ctx.emit(endpoint_name)
        self.counter += 1
