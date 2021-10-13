import os
import pytest
from typing import Dict
from exasol_sagemaker_extension.autopilot_training_udf import \
    AutopilotTrainingUDF

AWS_CONNECTION = "AWS_CONNECTION"
AWS_REGION = "eu-central-1"
AWS_ROLE = ""
AWS_S3_URI = ""
AWS_KEY_ID = ""
AWS_ACCESS_KEY = ""
AWS_SESSION_TOKEN = ""
os.environ["AWS_SESSION_TOKEN"] = AWS_SESSION_TOKEN


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


@pytest.mark.skipif(
    "AWS_SESSION_TOKEN" not in os.environ or not os.environ["AWS_SESSION_TOKEN"],
    reason="AWS_SESSION_TOKEN is not set")
def test_autopilot_training_udf_real():
    class Context:
        def __init__(self,
                     model_name: str,
                     aws_s3_connection: str,
                     aws_region: str,
                     role: str,
                     bucket: str,
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
            self.bucket = bucket
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

    ctx = Context(
        "test-model-name",
        AWS_CONNECTION,
        AWS_REGION,
        AWS_ROLE,
        'exasol-sagemaker-extension',
        'CLASS_POS',
        'BinaryClassification',
        '{"MetricName": "Accuracy"}',
        100,
        5,
        10
    )

    aws_s3_connection = Connection(
        address=AWS_S3_URI, user=AWS_KEY_ID, password=AWS_ACCESS_KEY)
    exa = ExaEnvironment({AWS_CONNECTION: aws_s3_connection})
    autopilot_training_udf_obj = AutopilotTrainingUDF(exa)
    autopilot_training_udf_obj.run(ctx)
    assert ctx.get_emitted()
