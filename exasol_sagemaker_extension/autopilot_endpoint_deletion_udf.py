import os
from typing import Callable
from exasol_sagemaker_extension.autopilot_utils.enpoint_deletion import \
    AutopilotEndpointDeletion


class AutopilotEndpointDeletionUDF:
    def __init__(self, exa,
                 delete_method: Callable = AutopilotEndpointDeletion.delete):
        self.exa = exa
        self.counter = 0
        self.delete_method = delete_method

    def run(self, ctx):
        endpoint_name = ctx.endpoint_name
        aws_s3_connection = ctx.aws_s3_connection
        aws_region = ctx.aws_region  # TODO

        aws_s3_conn_obj = self.exa.get_connection(aws_s3_connection)
        os.environ["AWS_DEFAULT_REGION"] = aws_region
        os.environ["AWS_ACCESS_KEY_ID"] = aws_s3_conn_obj.user
        os.environ["AWS_SECRET_ACCESS_KEY"] = aws_s3_conn_obj.password

        endpoint_name = self.delete_method(
            endpoint_name=endpoint_name
        )

        ctx.emit(endpoint_name)
        self.counter += 1
