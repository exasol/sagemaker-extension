import pytest
from tests.integration_tests.utils.parameters import aws_params, \
    reg_setup_params, cls_setup_params

INSTANCE_TYPE = "ml.m5.large"
INSTANCE_COUNT = 1


@pytest.mark.skipif(not aws_params.aws_access_key,
                    reason="AWS credentials are not set")
def test_deploy_sagemaker_autopilot_regression_endpoint(
        register_language_container, deploy_scripts, setup_database):
    _run_test(reg_setup_params, setup_database)


@pytest.mark.skipif(not aws_params.aws_access_key,
                    reason="AWS credentials are not set")
def test_deploy_sagemaker_autopilot_classification_endpoint(
        register_language_container, deploy_scripts, setup_database):
    _run_test(cls_setup_params, setup_database)


def _run_test(setup_params, db_conn):
    query_deployment = "EXECUTE SCRIPT " \
                       "{schema}.SME_DEPLOY_SAGEMAKER_AUTOPILOT_ENDPOINT(" \
                       "'{job_name}', '{endpoint_name}', '{schema}', " \
                       "'{instance_type}',  {instance_count}, " \
                       "'{aws_conn_name}', '{aws_region}')".\
        format(schema=setup_params.schema_name,
               job_name=setup_params.job_name,
               endpoint_name=setup_params.endpoint_name,
               instance_type=INSTANCE_TYPE,
               instance_count=INSTANCE_COUNT,
               aws_conn_name=aws_params.aws_conn_name,
               aws_region=aws_params.aws_region)

    db_conn.execute(query_deployment)

    query_scripts = "SELECT SCRIPT_NAME FROM SYS.EXA_ALL_SCRIPTS " \
                    "WHERE SCRIPT_SCHEMA = '{schema}'".\
        format(schema=setup_params.schema_name.upper())
    all_scripts = db_conn.execute(query_scripts).fetchall()
    prediction_udf_name = setup_params.endpoint_name
    assert prediction_udf_name in list(map(lambda x: x[0], all_scripts))

