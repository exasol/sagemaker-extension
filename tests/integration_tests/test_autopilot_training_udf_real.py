import pytest
from typing import Dict
from exasol_sagemaker_extension.autopilot_training_udf import \
    AutopilotTrainingUDF
from tests.integration_tests.utils.parameters import aws_params, \
    reg_setup_params, cls_setup_params


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
                 job_name: str,
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
        self.job_name = job_name
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


@pytest.mark.skipif(not aws_params.aws_access_key,
                    reason="AWS credentials are not set")
def test_autopilot_regression_training_udf_real():
    params_dict = {
        'setup_params': reg_setup_params,
        'problem_params': {
            "problem_type": "Regression",
            "objective": '{"MetricName":"MSE"}'}
    }
    _run_test(
        params_dict['setup_params'],
        params_dict['problem_params'])


@pytest.mark.skipif(not aws_params.aws_access_key,
                    reason="AWS credentials are not set")
def test_autopilot_classification_training_udf_real():
    params_dict = {
        'setup_params': cls_setup_params,
        'problem_params': {
            "problem_type": "BinaryClassification",
            "objective": '{"MetricName":"Accuracy"}'}
    }
    _run_test(
        params_dict['setup_params'],
        params_dict['problem_params'])


@pytest.mark.skipif(not aws_params.aws_access_key,
                    reason="AWS credentials are not set")
def test_autopilot_multi_classification_training_udf_real():
    params_dict = {
        'setup_params': cls_setup_params,
        'problem_params': {
            "problem_type": "MulticlassClassification",
            "objective": '{"MetricName":"Accuracy"}'}
    }
    _run_test(
        params_dict['setup_params'],
        params_dict['problem_params'])


def _run_test(setup_params, problem_params):
    ctx = Context(
        setup_params.job_name,
        aws_params.aws_conn_name,
        aws_params.aws_region,
        aws_params.aws_role,
        aws_params.aws_s3_uri,
        setup_params.aws_output_path,
        'OUTPUT_COL',
        problem_params['problem_type'],
        problem_params['objective'],
        None,
        2,
        None
    )

    aws_s3_connection = Connection(
        address=aws_params.aws_s3_uri,
        user=aws_params.aws_key_id,
        password=aws_params.aws_access_key)
    exa = ExaEnvironment({aws_params.aws_conn_name: aws_s3_connection})
    autopilot_training_udf_obj = AutopilotTrainingUDF(exa)
    autopilot_training_udf_obj.run(ctx)
    assert ctx.get_emitted()
