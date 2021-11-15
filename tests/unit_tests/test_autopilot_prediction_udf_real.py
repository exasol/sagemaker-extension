import json
import pytest
import pandas as pd
from typing import Dict

from exasol_sagemaker_extension.autopilot_prediction import \
    AutopilotPredictionUDF

JOB_NAME = "bostonhousing2"
ENDPOINT_NAME = "bostonhousing2endpoint"


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
    def __init__(self):
        self._emitted = []

    def emit(self, *args):
        self._emitted.append(args)

    def get_emitted(self):
        return self._emitted

    def get_dataframe(self):
        data = [
            (0.00632, 18.0, 2.31, 0.0, 0.538, 6.575, 65.2,
             4.09, 1.0, 296.0, 15.3, 396.9, 4.98),
            (0.02731, 0.0, 7.07, 0.0, 0.469, 6.421, 78.9,
             4.9671, 2.0, 242.0, 17.8, 396.9, 9.14)
        ]
        return pd.DataFrame(data=data)


def test_autopilot_endpoint_deployment_udf_real(get_real_params):
    if "AWS_ACCESS_KEY" not in get_real_params \
            or not get_real_params["AWS_ACCESS_KEY"]:
        pytest.skip("AWS credentials are not set")

    connection_data = {
        "aws_s3_connection": "AWS_CONNECTION",
        "aws_region": "eu-central-1",
        "name": ENDPOINT_NAME,
        "status": "deployed"
    }
    ctx = Context()

    aws_s3_connection = Connection(
        address=get_real_params["AWS_S3_URI"],
        user=get_real_params["AWS_KEY_ID"],
        password=get_real_params["AWS_ACCESS_KEY"])
    model_connection = Connection(
        address="",
        password=json.dumps(connection_data))

    exa = ExaEnvironment({
        get_real_params["AWS_CONNECTION"]: aws_s3_connection,
        JOB_NAME: model_connection})
    autopilot_prediction_obj = AutopilotPredictionUDF(exa, JOB_NAME)
    autopilot_prediction_obj.run(ctx)

    assert ctx.get_emitted()

