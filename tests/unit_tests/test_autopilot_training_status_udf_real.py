import os
import pytest
from typing import Dict
from exasol_sagemaker_extension.autopilot_training_status_udf import \
    AutopilotTrainingStatusUDF

MODEL_NAME = "TESTEXA"


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
    if "AWS_SESSION_TOKEN" not in os.environ or \
            not os.environ["AWS_SESSION_TOKEN"]:
        pytest.skip("AWS_SESSION_TOKEN is not set")

    class Context:
        def __init__(self,
                     model_name: str,
                     aws_s3_connection: str,
                     aws_region: str):
            self.model_name = model_name
            self.aws_s3_connection = aws_s3_connection
            self.aws_region = aws_region
            self._emitted = []

        def emit(self, *args):
            self._emitted.append(args)

        def get_emitted(self):
            return self._emitted

    ctx = Context(
        MODEL_NAME,
        get_real_params["AWS_CONNECTION"],
        get_real_params["AWS_REGION"]
    )

    aws_s3_connection = Connection(
        address=get_real_params["AWS_S3_URI"],
        user=get_real_params["AWS_KEY_ID"],
        password=get_real_params["AWS_ACCESS_KEY"])
    exa = ExaEnvironment({get_real_params["AWS_CONNECTION"]: aws_s3_connection})
    autopilot_training_status_udf_obj = AutopilotTrainingStatusUDF(exa)
    autopilot_training_status_udf_obj.run(ctx)
    assert ctx.get_emitted()
