import os
from exasol_udf_mock_python.group import Group
from exasol_udf_mock_python.column import Column
from exasol_udf_mock_python.connection import Connection
from exasol_udf_mock_python.mock_exa_environment import MockExaEnvironment
from exasol_udf_mock_python.mock_meta_data import MockMetaData
from exasol_udf_mock_python.udf_mock_executor import UDFMockExecutor

AWS_AUTOML_JOB_NAME = "test-model-name"
AWS_KEY_ID = "test_aws_key_id"
AWS_ACCESS_KEY = "test_aws_access_key"
AWS_REGION = "eu-central-1"
AWS_CONNECTION_NAME = "S3_CONNECTION"
AWS_S3_URI = f"https://127.0.0.1:4566"
JOB_STATUS = "InProgress"
JOB_SECONDARY_STATUS = "Feature Engineering"


def udf_wrapper():
    from exasol_udf_mock_python.udf_context import UDFContext
    from exasol_sagemaker_extension.autopilot_training_status_udf \
        import AutopilotTrainingStatusUDF

    def mocked_check_training_status_method(model_name: str):
        return "InProgress", "Feature Engineering"

    udf = AutopilotTrainingStatusUDF(
        exa, check_training_status_method=mocked_check_training_status_method)

    def run(ctx: UDFContext):
        udf.run(ctx)


def create_mock_metadata():
    meta = MockMetaData(
        script_code_wrapper_function=udf_wrapper,
        input_type="SET",
        input_columns=[
            Column("model_name", str, "VARCHAR(2000000)"),
            Column("aws_s3_connection", str, "VARCHAR(2000000)"),
            Column("aws_region", str, "VARCHAR(2000000)")
        ],
        output_type="EMIT",
        output_columns=[
            Column("job_status", str, "VARCHAR(2000000)"),
            Column("job_secondary_status", str, "VARCHAR(2000000)")
        ]
    )
    return meta


def test_autopilot_training_status_udf_mock():
    executor = UDFMockExecutor()
    meta = create_mock_metadata()
    aws_s3_connection = Connection(
        address=AWS_S3_URI, user=AWS_KEY_ID, password=AWS_ACCESS_KEY)
    exa = MockExaEnvironment(
        meta, connections={AWS_CONNECTION_NAME: aws_s3_connection})

    input_data = (
        "test_model_name",
        AWS_CONNECTION_NAME,
        AWS_REGION,
    )

    result = executor.run([Group([input_data])], exa)
    for i, group in enumerate(result):
        result_row = group.rows
        assert len(result_row) == 1
        job_status = result_row[0][0]
        job_secondary_status = result_row[0][1]
        assert job_status == JOB_STATUS
        assert job_secondary_status == JOB_SECONDARY_STATUS
        assert os.environ["AWS_ACCESS_KEY_ID"] == AWS_KEY_ID
        assert os.environ["AWS_SECRET_ACCESS_KEY"] == AWS_ACCESS_KEY
        assert os.environ["AWS_DEFAULT_REGION"] == AWS_REGION
