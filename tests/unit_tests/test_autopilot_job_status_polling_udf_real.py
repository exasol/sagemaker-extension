import pytest
from typing import Dict
from exasol_sagemaker_extension.autopilot_job_status_polling_udf import \
    AutopilotJobStatusPollingUDF

JOB_NAME = "end2end-27Oct21-0722"


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


def test_autopilot_training_status_udf_real(get_real_params):
    if "AWS_ACCESS_KEY" not in get_real_params \
            or not get_real_params["AWS_ACCESS_KEY"]:
        pytest.skip("AWS credentials are not set")

    class Context:
        def __init__(self,
                     job_name: str,
                     aws_s3_connection: str,
                     aws_region: str):
            self.job_name = job_name
            self.aws_s3_connection = aws_s3_connection
            self.aws_region = aws_region
            self._emitted = []

        def emit(self, *args):
            self._emitted.append(args)

        def get_emitted(self):
            return self._emitted

    ctx = Context(
        JOB_NAME,
        get_real_params["AWS_CONNECTION"],
        get_real_params["AWS_REGION"]
    )

    aws_s3_connection = Connection(
        address=get_real_params["AWS_S3_URI"],
        user=get_real_params["AWS_KEY_ID"],
        password=get_real_params["AWS_ACCESS_KEY"])
    exa = ExaEnvironment({get_real_params["AWS_CONNECTION"]: aws_s3_connection})
    autopilot_training_status_udf_obj = AutopilotJobStatusPollingUDF(exa)
    autopilot_training_status_udf_obj.run(ctx)
    assert ctx.get_emitted()
