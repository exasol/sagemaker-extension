import json
import pytest
import pandas as pd
from typing import Dict
from exasol_sagemaker_extension.autopilot_prediction import \
    AutopilotPredictionUDF
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
    def __init__(self):
        self._emitted = []

    def emit(self, *args):
        self._emitted.append(args)

    def get_emitted(self):
        return self._emitted

    def get_dataframe(self):
        data = [
            (1.1, 1.2),
            (2.2, 2.4),
            (3.3, 3.6)
        ]
        return pd.DataFrame(data=data)


@pytest.mark.skipif(not aws_params.aws_access_key,
                    reason="AWS credentials are not set")
def test_autopilot_endpoint_deployment_udf_real():
    connection_data = {
        "aws_s3_connection": setup_params.aws_conn_name,
        "aws_region": aws_params.aws_region,
        "endpoint_name": setup_params.endpoint_name,
        "status": "deployed"
    }
    ctx = Context()

    aws_s3_connection = Connection(
        address=aws_params.aws_s3_uri,
        user=aws_params.aws_key_id,
        password=aws_params.aws_access_key)
    model_connection = Connection(
        address=json.dumps(connection_data))

    exa = ExaEnvironment({
        setup_params.aws_conn_name: aws_s3_connection,
        setup_params.job_name: model_connection})
    autopilot_prediction_obj = AutopilotPredictionUDF(exa, setup_params.job_name)
    autopilot_prediction_obj.run(ctx)

    print(ctx.get_emitted())
    assert ctx.get_emitted()

