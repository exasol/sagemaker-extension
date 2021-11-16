import os
from exasol_udf_mock_python.group import Group
from exasol_udf_mock_python.column import Column
from exasol_udf_mock_python.connection import Connection
from exasol_udf_mock_python.mock_exa_environment import MockExaEnvironment
from exasol_udf_mock_python.mock_meta_data import MockMetaData
from exasol_udf_mock_python.udf_mock_executor import UDFMockExecutor


JOB_NAME = "testModel"
ENDPOINT_NAME = "testEndpoint"
INSTANCE_TYPE = "ml.m5.large"
INSTANCE_COUNT = 1


def udf_wrapper():
    from exasol_udf_mock_python.udf_context import UDFContext
    from exasol_sagemaker_extension.autopilot_endpoint_deployment_udf import \
        AutopilotEndpointDeploymentUDF

    def mocked_deploy_method(**kwargs):
        return "test-model-name"

    udf = AutopilotEndpointDeploymentUDF(exa, deploy_method=mocked_deploy_method)

    def run(ctx: UDFContext):
        udf.run(ctx)


def create_mock_metadata():
    meta = MockMetaData(
        script_code_wrapper_function=udf_wrapper,
        input_type="SET",
        input_columns=[
            Column("job_name", str, "VARCHAR(2000000)"),
            Column("endpoint_name", str, "VARCHAR(2000000)"),
            Column("instance_type", str, "VARCHAR(2000000)"),
            Column("instance_count", int, "INTEGER"),
            Column("aws_s3_connection", str, "VARCHAR(2000000)"),
            Column("aws_region", str, "VARCHAR(2000000)")
        ],
        output_type="EMIT",
        output_columns=[
            Column("endpoint_name", str, "VARCHAR(2000000)")
        ]
    )
    return meta


def test_autopilot_training_udf_mock(get_mock_aws_params):
    executor = UDFMockExecutor()
    meta = create_mock_metadata()
    aws_s3_connection = Connection(
        address=get_mock_aws_params["AWS_S3_URI"],
        user=get_mock_aws_params["AWS_KEY_ID"],
        password=get_mock_aws_params["AWS_ACCESS_KEY"])
    exa = MockExaEnvironment(
        meta,
        connections={get_mock_aws_params["AWS_CONNECTION_NAME"]: aws_s3_connection})

    input_data = (
        JOB_NAME,
        ENDPOINT_NAME,
        INSTANCE_TYPE,
        INSTANCE_COUNT,
        get_mock_aws_params["AWS_CONNECTION_NAME"],
        get_mock_aws_params["AWS_REGION"]
    )

    result = executor.run([Group([input_data])], exa)
    for i, group in enumerate(result):
        result_row = group.rows
        assert len(result_row) == 1
        job_name = result_row[0][0]
        assert job_name == \
               get_mock_aws_params["AWS_AUTOML_JOB_NAME"]
        assert os.environ["AWS_ACCESS_KEY_ID"] == \
               get_mock_aws_params["AWS_KEY_ID"]
        assert os.environ["AWS_SECRET_ACCESS_KEY"] == \
               get_mock_aws_params["AWS_ACCESS_KEY"]
        assert os.environ["AWS_DEFAULT_REGION"] == \
               get_mock_aws_params["AWS_REGION"]
