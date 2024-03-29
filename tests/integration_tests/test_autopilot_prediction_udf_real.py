import json
import pytest
import pandas as pd
from typing import Dict
from exasol_sagemaker_extension.autopilot_prediction_udf import \
    AutopilotPredictionUDF
from tests.integration_tests.utils.parameters import aws_params, \
    reg_setup_params, cls_setup_params


class Connection:
    def __init__(self, address: str, user: str = None, password: str = None):
        self.address = address
        self.user = user
        self.password = password


class Column:
    def __init__(self, name, type, sql_type):
        self.name = name
        self.type = type
        self.sql_type = sql_type


class MetaData:
    def __init__(self, input_columns, output_columns):
        self.input_columns = input_columns
        self.output_columns = output_columns


class ExaEnvironment:
    def __init__(self, connections: Dict[str, Connection] = None,
                 meta: MetaData = None ):
        self._connections = connections
        self.meta = meta
        if self._connections is None:
            self._connections = {}

    def get_connection(self, name: str) -> Connection:
        return self._connections[name]


class Context:
    def __init__(self):
        self._emitted = []
        self._is_accessed_once = False

    def emit(self, *args):
        self._emitted.append(args)

    def get_emitted(self):
        return self._emitted

    def get_dataframe(self, num_rows='all'):
        data = [
            (1.1, 1.2),
            (2.2, 2.4),
            (3.3, 3.6)
        ]
        return_df = None if self._is_accessed_once else pd.DataFrame(data=data)
        self._is_accessed_once = True
        return return_df


@pytest.mark.skipif(not aws_params.aws_secret_access_key,
                    reason="AWS credentials are not set")
def test_regression_autopilot_prediction_udf_real():
    connection_data = {
        "aws_s3_connection": aws_params.aws_conn_name,
        "aws_region": aws_params.aws_region,
        "endpoint_name": reg_setup_params.endpoint_name,
        "status": "deployed",
        "batch_size": reg_setup_params.batch_size
    }
    ctx = Context()

    aws_s3_connection = Connection(
        address=aws_params.aws_s3_uri,
        user=aws_params.aws_access_key_id,
        password=aws_params.aws_secret_access_key)
    model_connection = Connection(
        address=json.dumps(connection_data))

    input_cols = [
        Column("COL_1", float, "FLOAT"),
        Column("COL_2", float, "FLOAT")]
    meta = MetaData(
        input_columns=input_cols,
        output_columns=input_cols + [Column("OUTPUT_COL", float, "FLOAT")])
    exa = ExaEnvironment(
        connections={
            aws_params.aws_conn_name: aws_s3_connection,
            reg_setup_params.job_name: model_connection},
        meta=meta)
    autopilot_prediction_obj = AutopilotPredictionUDF(
        exa, reg_setup_params.job_name)
    autopilot_prediction_obj.run(ctx)

    print(ctx.get_emitted())
    assert ctx.get_emitted()
    assert ctx.get_emitted()[0][0].shape == (3, 3)


@pytest.mark.skipif(not aws_params.aws_secret_access_key,
                    reason="AWS credentials are not set")
def test_classification_autopilot_prediction_udf_real():
    connection_data = {
        "aws_s3_connection": aws_params.aws_conn_name,
        "aws_region": aws_params.aws_region,
        "endpoint_name": cls_setup_params.endpoint_name,
        "status": "deployed",
        "batch_size": cls_setup_params.batch_size
    }
    ctx = Context()

    aws_s3_connection = Connection(
        address=aws_params.aws_s3_uri,
        user=aws_params.aws_access_key_id,
        password=aws_params.aws_secret_access_key)
    model_connection = Connection(
        address=json.dumps(connection_data))

    input_cols = [
        Column("COL_1", float, "FLOAT"),
        Column("COL_2", float, "FLOAT")]
    output_cols = [
        Column("PROBABILITY", float, "FLOAT"),
        Column("OUTPUT_COL", float, "FLOAT")]
    meta = MetaData(
        input_columns=input_cols,
        output_columns=input_cols + output_cols)
    exa = ExaEnvironment(
        connections={
            aws_params.aws_conn_name: aws_s3_connection,
            cls_setup_params.job_name: model_connection},
        meta=meta)
    autopilot_prediction_obj = AutopilotPredictionUDF(
        exa, cls_setup_params.job_name)
    autopilot_prediction_obj.run(ctx)

    print(ctx.get_emitted())
    assert ctx.get_emitted()
    assert ctx.get_emitted()[0][0].shape == (3, 4)
