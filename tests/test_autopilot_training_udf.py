import os
from exasol_udf_mock_python.group import Group
from exasol_udf_mock_python.column import Column
from exasol_udf_mock_python.connection import Connection
from exasol_udf_mock_python.mock_exa_environment import MockExaEnvironment
from exasol_udf_mock_python.mock_meta_data import MockMetaData
from exasol_udf_mock_python.udf_mock_executor import UDFMockExecutor

AWS_AUTOML_JOB_NAME = "test_job_name"
AWS_KEY_ID = "test_aws_key_id"
AWS_ACCESS_KEY = "test_aws_access_key"
AWS_REGION = "eu-central-1"
AWS_SESSION_TOKEN = "test_aws_session_token"
AWS_S3_URI = "https://127.0.0.1:4566"
AWS_CONNECTION_NAME = "S3_CONNECTION"
AWS_BUCKET_NAME = "integrationtestbucket"


def udf_wrapper():
    from exasol_udf_mock_python.udf_context import UDFContext
    from exasol_sagemaker_extension.autopilot_training_udf import AutopilotTrainingUDF

    def mocked_training_method(**kwargs):
        return "test_job_name"

    udf = AutopilotTrainingUDF(exa, training_method=mocked_training_method)

    def run(ctx: UDFContext):
        udf.run(ctx)


def create_mock_metadata():
    meta = MockMetaData(
        script_code_wrapper_function=udf_wrapper,
        input_type="SET",
        input_columns=[
            Column("aws_s3_connection", str, "VARCHAR(2000000)"),
            Column("aws_session_token", str, "VARCHAR(2000000)"),
            Column("aws_region", str, "VARCHAR(2000000)"),
            Column("role", str, "VARCHAR(2000000)"),
            Column("bucket", str, "VARCHAR(2000000)"),
            Column("target_attribute_name", str, "VARCHAR(2000000)"),
            Column("problem_type", str, "VARCHAR(2000000)"),
            Column("max_runtime_for_automl_job_in_seconds", int, "INTEGER"),
            Column("max_candidates", int, "INTEGER"),
            Column("max_runtime_per_training_job_in_seconds", int, "INTEGER"),
        ],
        output_type="EMIT",
        output_columns=[
            Column("job_name", str, "VARCHAR(2000000)")
        ]
    )
    return meta


def test_autopilot_training_udf():
    executor = UDFMockExecutor()
    meta = create_mock_metadata()

    aws_connections_map = {
        "no_session_token_standart_pasword": Connection(
            address=AWS_S3_URI, user=AWS_KEY_ID, password=AWS_ACCESS_KEY),
        "no_session_token_json_password": Connection(
            address=AWS_S3_URI, user=AWS_KEY_ID,
            password='{{"secret_key" : "{0}"}}'.format(
                AWS_ACCESS_KEY)),
        "session_token_json_password":
            Connection(address=AWS_S3_URI, user=AWS_KEY_ID,
                       password='{{"secret_key" : "{0}", '
                                '"session_token" : "{1}"}}'.format(
                           AWS_ACCESS_KEY, AWS_SESSION_TOKEN))
    }

    input_data = (
            AWS_CONNECTION_NAME,
            "aws_session_token",
            AWS_REGION,
            "role_sagemaker_executor",
            AWS_BUCKET_NAME,
            "target_name",
            "problem_type",
            100,
            5,
            10
    )

    for key, conn in aws_connections_map.items():
        exa = MockExaEnvironment(meta, connections={AWS_CONNECTION_NAME: conn})
        result = executor.run([Group([input_data])], exa)
        for i, group in enumerate(result):
            result_row = group.rows
            assert len(result_row) == 1
            job_name = result_row[0][0]
            assert job_name == AWS_AUTOML_JOB_NAME
            assert os.environ["AWS_ACCESS_KEY_ID"] == AWS_KEY_ID
            assert os.environ["AWS_SECRET_ACCESS_KEY"] == AWS_ACCESS_KEY
            assert os.environ["AWS_DEFAULT_REGION"] == AWS_REGION

            if 'no' in key:
                assert "AWS_SESSION_KEY" not in os.environ
            else:
                assert os.environ["AWS_SESSION_TOKEN"] == AWS_SESSION_TOKEN





