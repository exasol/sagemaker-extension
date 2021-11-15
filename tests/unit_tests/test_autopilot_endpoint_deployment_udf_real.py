import pytest
from typing import Dict
from exasol_sagemaker_extension.autopilot_endpoint_deployment_udf import \
    AutopilotEndpointDeploymentUDF


JOB_NAME = "bostonhousing2"
ENDPOINT_NAME = "bostonhousing2endpoint"
INSTANCE_TYPE = "ml.m5.large"
INSTANCE_COUNT = 1


class Connection:
    def __init__(self, address: str, user: str = None, password: str = None):
        self.address = address
        self.user = user
        self.password = password


class ExaEnvironment:
    def __init__(self, connections: Dict[str, Connection] = None):
        self._connections = connections
        if self._connections is None:
            self._connections = {}

    def get_connection(self, name: str) -> Connection:
        return self._connections[name]


class Context:
    def __init__(self,
                 job_name: str,
                 endpoint_name: str,
                 instance_type: str,
                 instance_count: int,
                 aws_s3_connection: str,
                 aws_region: str):
        self.job_name = job_name
        self.endpoint_name = endpoint_name
        self.instance_type = instance_type
        self.instance_count = instance_count
        self.aws_s3_connection = aws_s3_connection
        self.aws_region = aws_region
        self._emitted = []

    def emit(self, *args):
        self._emitted.append(args)

    def get_emitted(self):
        return self._emitted


def test_autopilot_endpoint_deployment_udf_real(get_real_params):
    if "AWS_ACCESS_KEY" not in get_real_params \
            or not get_real_params["AWS_ACCESS_KEY"]:
        pytest.skip("AWS credentials are not set")

    ctx = Context(
        JOB_NAME,
        ENDPOINT_NAME,
        INSTANCE_TYPE,
        INSTANCE_COUNT,
        get_real_params["AWS_CONNECTION"],
        get_real_params["AWS_REGION"]
    )

    aws_s3_connection = Connection(
        address=get_real_params["AWS_S3_URI"],
        user=get_real_params["AWS_KEY_ID"],
        password=get_real_params["AWS_ACCESS_KEY"])
    exa = ExaEnvironment({get_real_params["AWS_CONNECTION"]: aws_s3_connection})
    autopilot_endpoint_deployment_obj = AutopilotEndpointDeploymentUDF(exa)
    autopilot_endpoint_deployment_obj.run(ctx)
    assert ctx.get_emitted()
