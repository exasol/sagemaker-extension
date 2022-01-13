import json
import pytest
from tests.integration_tests.utils.parameters import aws_params, \
    reg_setup_params, cls_setup_params


@pytest.mark.skipif(not aws_params.aws_access_key,
                    reason="AWS credentials are not set")
def test_train_with_sagemaker_autopilot_regression_job(
        register_language_container, deploy_scripts, setup_database):

    params_dict = {
        'setup_params': reg_setup_params,
        'problem_params': {
            "problem_type": "Regression",
            "objective": '{"MetricName":"MSE"}'}
    }
    _run_test(
        params_dict['setup_params'],
        params_dict['problem_params'],
        setup_database)


@pytest.mark.skipif(not aws_params.aws_access_key,
                    reason="AWS credentials are not set")
def test_train_with_sagemaker_autopilot_classification_job(
        register_language_container, deploy_scripts, setup_database):

    params_dict = {
        'setup_params': cls_setup_params,
        'problem_params': {
            "problem_type": "BinaryClassification",
            "objective": '{"MetricName":"F1"}'}
    }
    _run_test(
        params_dict['setup_params'],
        params_dict['problem_params'],
        setup_database)


def _run_test(setup_params, problem_params, db_conn):
    params_dict = {
        "job_name"							: setup_params.job_name,
        "aws_credentials_connection_name"	: aws_params.aws_conn_name,
        "aws_region"						: aws_params.aws_region,
        "iam_sagemaker_role"				: aws_params.aws_role,
        "s3_bucket_uri"						: aws_params.aws_s3_uri,
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
    assert setup_params.job_name in list(map(lambda x: x[0], all_jobs))
