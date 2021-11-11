import os
import pytest
from typing import Dict
from exasol_sagemaker_extension.autopilot_training_udf import \
    AutopilotTrainingUDF


MODEL_NAME = "end2endmodel"


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
    def __init__(self,
                 model_name: str,
                 aws_s3_connection: str,
                 aws_region: str,
                 role: str,
                 s3_bucket_uri: str,
                 s3_output_path: str,
                 target_attribute_name: str,
                 problem_type: str,
                 objective: str,
                 max_runtime_for_automl_job_in_seconds: int,
                 max_candidates: int,
                 max_runtime_per_training_job_in_seconds: int):
        self.model_name = model_name
        self.aws_s3_connection = aws_s3_connection
        self.aws_region = aws_region
        self.role = role
        self.s3_bucket_uri = s3_bucket_uri
        self.s3_output_path = s3_output_path
        self.target_attribute_name = target_attribute_name
        self.problem_type = problem_type
        self.objective = objective
        self.max_runtime_for_automl_job_in_seconds = \
            max_runtime_for_automl_job_in_seconds
        self.max_candidates = max_candidates
        self.max_runtime_per_training_job_in_seconds = \
            max_runtime_per_training_job_in_seconds
        self._emitted = []

    def emit(self, *args):
        self._emitted.append(args)

    def get_emitted(self):
        return self._emitted


def test_autopilot_training_udf_real(get_real_params):
    if "AWS_ACCESS_KEY" not in get_real_params \
            or not get_real_params["AWS_ACCESS_KEY"]:
        pytest.skip("AWS credentials are not set")

    ctx = Context(
        MODEL_NAME,
        get_real_params["AWS_CONNECTION"],
        get_real_params["AWS_REGION"],
        get_real_params["AWS_ROLE"],
        get_real_params["AWS_S3_URI"],
        get_real_params["AWS_OUTPUT_PATH"],
        'IDX',
        'BinaryClassification',
        '{"MetricName": "Accuracy"}',
        100,
        5,
        10
    )

    aws_s3_connection = Connection(
        address=get_real_params["AWS_S3_URI"],
        user=get_real_params["AWS_KEY_ID"],
        password=get_real_params["AWS_ACCESS_KEY"])
    exa = ExaEnvironment({get_real_params["AWS_CONNECTION"]: aws_s3_connection})
    autopilot_training_udf_obj = AutopilotTrainingUDF(exa)
    autopilot_training_udf_obj.run(ctx)
    assert ctx.get_emitted()
