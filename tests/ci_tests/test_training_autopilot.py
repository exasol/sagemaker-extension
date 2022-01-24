import os
import json
import pytest
from datetime import datetime
from tests.ci_tests.utils.checkers import is_aws_credentials_not_set
from tests.ci_tests.utils.parameters import reg_model_setup_params, aws_params, \
    cls_model_setup_params

curr_datetime = datetime.now().strftime("%y%m%d%H%M%S")


@pytest.mark.skipif("is_aws_credentials_not_set() == True",
                    reason="AWS credentials are not set")
def test_train_autopilot_regression_job(setup_ci_test_environment):
    problem_params = {
        "problem_type": "Regression",
        "objective": '{"MetricName":"MSE"}'}

    _run_test(
        reg_model_setup_params,
        problem_params,
        setup_ci_test_environment)


@pytest.mark.skipif("is_aws_credentials_not_set() == True",
                    reason="AWS credentials are not set")
def test_train_autopilot_classification_job(setup_ci_test_environment):
    problem_params = {
        "problem_type": "BinaryClassification",
        "objective": '{"MetricName":"F1"}'}

    _run_test(
        cls_model_setup_params,
        problem_params,
        setup_ci_test_environment)


def _run_test(setup_params, problem_params, db_conn):
    model_name = ''.join((setup_params.model_type, curr_datetime))
    job_name = ''.join((model_name, 'job'))

    params_dict = {
        "job_name"							: job_name,
        "aws_credentials_connection_name"	: aws_params.aws_conn_name,
        "aws_region"						: os.environ["AWS_REGION"],
        "iam_sagemaker_role"				: os.environ["AWS_ROLE"],
        "s3_bucket_uri"						: aws_params.aws_bucket_uri,
        "s3_output_path"					: setup_params.aws_output_path,
        "input_schema_name"					: setup_params.schema_name,
        "input_table_or_view_name"			: setup_params.table_name,
        "target_attribute_name"				: setup_params.target_col,
        "max_candidates"					: 2,
    }
    params_dict = {**params_dict, **problem_params}

    query_training = "EXECUTE SCRIPT " \
                     "{schema}.SME_TRAIN_WITH_SAGEMAKER_AUTOPILOT('{params}')".\
        format(schema=setup_params.schema_name, params=json.dumps(params_dict))
    db_conn.execute(query_training)

    query_metadata = "SELECT JOB_NAME FROM " \
                     "{schema}.SME_METADATA_AUTOPILOT_JOBS".\
        format(schema=setup_params.schema_name)

    all_jobs = db_conn.execute(query_metadata).fetchall()
    assert job_name in list(map(lambda x: x[0], all_jobs))