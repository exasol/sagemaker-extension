import os
from exasol_udf_mock_python.group import Group
from exasol_udf_mock_python.column import Column
from exasol_udf_mock_python.connection import Connection
from exasol_udf_mock_python.mock_exa_environment import MockExaEnvironment
from exasol_udf_mock_python.mock_meta_data import MockMetaData
from exasol_udf_mock_python.udf_mock_executor import UDFMockExecutor


JOB_NAME = "test_model_name"


def udf_wrapper():
    from exasol_udf_mock_python.udf_context import UDFContext
    from exasol_sagemaker_extension.autopilot_training_udf import AutopilotTrainingUDF

    def mocked_training_method(**kwargs):
        return "test-model-name"

    udf = AutopilotTrainingUDF(exa, training_method=mocked_training_method)

    def run(ctx: UDFContext):
        udf.run(ctx)


def create_mock_metadata():
    meta = MockMetaData(
        script_code_wrapper_function=udf_wrapper,
        input_type="SET",
        input_columns=[
            Column("job_name", str, "VARCHAR(2000000)"),
            Column("aws_s3_connection", str, "VARCHAR(2000000)"),
            Column("aws_region", str, "VARCHAR(2000000)"),
            Column("role", str, "VARCHAR(2000000)"),
            Column("s3_bucket_uri", str, "VARCHAR(2000000)"),
            Column("s3_output_path", str, "VARCHAR(2000000)"),
            Column("target_attribute_name", str, "VARCHAR(2000000)"),
            Column("problem_type", str, "VARCHAR(2000000)"),
            Column("objective", str, "VARCHAR(2000000)"),
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


def test_autopilot_training_udf_mock(get_mock_params):
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
        JOB_NAME,
        get_mock_params["AWS_CONNECTION_NAME"],
        get_mock_params["AWS_REGION"],
        get_mock_params["AWS_SAGEMAKER_ROLE"],
        get_mock_params["AWS_BUCKET_URI"],
        get_mock_params["AWS_OUTPUT_PATH"],
        "CLASS_POS",
        "BinaryClassification",
        '{"MetricName": "Accuracy"}',
        100,
        5,
        10
    )

    result = executor.run([Group([input_data])], exa)
    for i, group in enumerate(result):
        result_row = group.rows
        assert len(result_row) == 1
        job_name = result_row[0][0]
        assert job_name == \
               get_mock_params["AWS_AUTOML_JOB_NAME"]
        assert os.environ["AWS_ACCESS_KEY_ID"] == \
               get_mock_params["AWS_KEY_ID"]
        assert os.environ["AWS_SECRET_ACCESS_KEY"] == \
               get_mock_params["AWS_ACCESS_KEY"]
        assert os.environ["AWS_DEFAULT_REGION"] == \
               get_mock_params["AWS_REGION"]
