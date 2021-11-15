import os

import pandas as pd
from exasol_udf_mock_python.group import Group
from exasol_udf_mock_python.column import Column
from exasol_udf_mock_python.connection import Connection
from exasol_udf_mock_python.mock_exa_environment import MockExaEnvironment
from exasol_udf_mock_python.mock_meta_data import MockMetaData
from exasol_udf_mock_python.udf_mock_executor import UDFMockExecutor


ENDPOINT_NAME = "test_model_name"


def udf_wrapper():
    from exasol_udf_mock_python.udf_context import UDFContext
    from exasol_sagemaker_extension.autopilot_prediction import \
        AutopilotPredictionUDF

    def mocked_prediction_method(endpoint_name: str, data_df: pd.DataFrame):
        return "predicted"

    udf = AutopilotPredictionUDF(
        exa, prediction_method=mocked_prediction_method)

    def run(ctx: UDFContext):
        udf.run(ctx)


def create_mock_metadata():
    meta = MockMetaData(
        script_code_wrapper_function=udf_wrapper,
        input_type="SET",
        input_columns=[
            Column("endpoint_name", str, "VARCHAR(2000000)"),
            Column("aws_s3_connection", str, "VARCHAR(2000000)"),
            Column("aws_region", str, "VARCHAR(2000000)")
        ],
        output_type="EMIT",
        output_columns=[
            Column("endpoint_name", str, "VARCHAR(2000000)")
        ]
    )
    return meta


def test_autopilot_endpoint_deletion_udf_mock(get_mock_params):
    executor = UDFMockExecutor()
    meta = create_mock_metadata()
    aws_s3_connection = Connection(
        address=get_mock_params["AWS_S3_URI"],
        user=get_mock_params["AWS_KEY_ID"],
        password=get_mock_params["AWS_ACCESS_KEY"])
    exa = MockExaEnvironment(
        meta,
        connections={get_mock_params["AWS_CONNECTION_NAME"]: aws_s3_connection})

    input_data = (
        ENDPOINT_NAME,
        get_mock_params["AWS_CONNECTION_NAME"],
        get_mock_params["AWS_REGION"],
    )

    result = executor.run([Group([input_data])], exa)
    for i, group in enumerate(result):
        result_row = group.rows
        assert len(result_row) == 1
        assert os.environ["AWS_ACCESS_KEY_ID"] == \
               get_mock_params["AWS_KEY_ID"]
        assert os.environ["AWS_SECRET_ACCESS_KEY"] == \
               get_mock_params["AWS_ACCESS_KEY"]
        assert os.environ["AWS_DEFAULT_REGION"] == \
               get_mock_params["AWS_REGION"]
