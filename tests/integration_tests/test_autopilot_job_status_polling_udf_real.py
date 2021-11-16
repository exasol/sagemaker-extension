import pytest
from typing import Dict
from exasol_sagemaker_extension.autopilot_job_status_polling_udf import \
    AutopilotJobStatusPollingUDF
from tests.integration_tests.utils.parameters import aws_params, setup_params


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


@pytest.mark.skipif(not aws_params.aws_access_key,
                    reason="AWS credentials are not set")
def test_autopilot_training_status_udf_real():
    ctx = Context(
        setup_params.job_name,
        setup_params.aws_conn_name,
        aws_params.aws_region
    )

    aws_s3_connection = Connection(
        address=aws_params.aws_s3_uri,
        user=aws_params.aws_key_id,
        password=aws_params.aws_access_key)
    exa = ExaEnvironment({setup_params.aws_conn_name: aws_s3_connection})
    autopilot_training_status_udf_obj = AutopilotJobStatusPollingUDF(exa)
    autopilot_training_status_udf_obj.run(ctx)

    assert ctx.get_emitted()
