import pytest
from tests.integration_tests.utils.parameters import aws_params, setup_params


@pytest.mark.skipif(not aws_params.aws_access_key,
                    reason="AWS credentials are not set")
def test_poll_sagemaker_autopilot_job_status(
        register_language_container, deploy_scripts, setup_database):

    db_conn = setup_database
    query_polling = "EXECUTE SCRIPT " \
                    "{schema}.SME_POLL_SAGEMAKER_AUTOPILOT_JOB_STATUS(" \
                    "'{job_name}', '{aws_conn_name}', '{aws_region}')".\
        format(schema=setup_params.schema_name,
               job_name=setup_params.job_name,
               aws_conn_name=setup_params.aws_conn_name,
               aws_region=aws_params.aws_region)

    status = db_conn.execute(query_polling).fetchall()
    assert len(status) == 1
    assert len(status[0]) == 2
