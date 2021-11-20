import os
import json
import numpy as np
from exasol_udf_mock_python.group import Group
from exasol_udf_mock_python.column import Column
from exasol_udf_mock_python.connection import Connection
from exasol_udf_mock_python.mock_exa_environment import MockExaEnvironment
from exasol_udf_mock_python.mock_meta_data import MockMetaData
from exasol_udf_mock_python.udf_mock_executor import UDFMockExecutor


ENDPOINT_NAME = "test_model_name"


def udf_wrapper():
    import pandas as pd
    from exasol_udf_mock_python.udf_context import UDFContext
    from exasol_sagemaker_extension.autopilot_prediction import \
        AutopilotPredictionUDF

    class MockedAutopilotPrediction:
        def __init__(self, endpoint_name):
            pass

        def predict(self, data_df: pd.DataFrame):
            return data_df.mean(axis=1)

    udf = AutopilotPredictionUDF(
        exa, "aws_s3_connection", prediction_class=MockedAutopilotPrediction)

    def run(ctx: UDFContext):
        udf.run(ctx)


def create_mock_metadata():
    input_columns = [
            Column("COL_1", float, "FLOAT"),
            Column("COL_2", float, "FLOAT"),
            Column("COL_3", float, "FLOAT")]
    meta = MockMetaData(
        script_code_wrapper_function=udf_wrapper,
        input_type="SET",
        input_columns=input_columns,
        output_type="EMIT",
        output_columns=input_columns + [
            Column("OUT", float, "FLOAT")
        ]
    )
    return meta


def test_autopilot_endpoint_deletion_udf_mock(get_mock_aws_params):
    executor = UDFMockExecutor()
    meta = create_mock_metadata()
    aws_s3_connection = Connection(
        address=get_mock_aws_params["AWS_S3_URI"],
        user=get_mock_aws_params["AWS_KEY_ID"],
        password=get_mock_aws_params["AWS_ACCESS_KEY"])

    connection_data = {
        "aws_s3_connection": get_mock_aws_params["AWS_CONNECTION_NAME"],
        "aws_region": "eu-central-1",
        "endpoint_name": ENDPOINT_NAME,
        "status": "deployed"
    }
    model_connection = Connection(
        address=json.dumps(connection_data))

    exa = MockExaEnvironment(meta, connections={
        get_mock_aws_params["AWS_CONNECTION_NAME"]: aws_s3_connection,
        'aws_s3_connection': model_connection
    })

    data_list = [(1.0, 2.0, 3.0), (11.0, 22.0, 33.0)]
    input_data = [Group(data_list)]
    result = executor.run(input_data, exa)
    for i, group in enumerate(result):
        result_row = group.rows
        assert len(result_row) == len(data_list)
        assert set(np.mean(data_list, axis=1)) == \
               set(map(lambda x: x[-1], result_row))
        assert os.environ["AWS_ACCESS_KEY_ID"] == \
               get_mock_aws_params["AWS_KEY_ID"]
        assert os.environ["AWS_SECRET_ACCESS_KEY"] == \
               get_mock_aws_params["AWS_ACCESS_KEY"]
        assert os.environ["AWS_DEFAULT_REGION"] == \
               get_mock_aws_params["AWS_REGION"]
