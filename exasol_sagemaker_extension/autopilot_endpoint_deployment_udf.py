import os
import json
from typing import Callable
from datetime import datetime

from exasol_sagemaker_extension import autopilot_handler


class AutopilotEndpointDeploymentUDF:
    def __init__(self, exa,
                 deploy_method: Callable =
                 autopilot_handler.deploy_endpoint):
        self.exa = exa
        self.counter = 0
        self.deploy_method = deploy_method

    def run(self, ctx):
        job_name = ctx.job_name
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
            instance_type=instance_type,
            instance_count=instance_count
        )

        ctx.emit(endpoint_name)
        self.counter += 1
