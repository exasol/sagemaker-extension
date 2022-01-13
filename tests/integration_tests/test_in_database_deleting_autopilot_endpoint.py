import pytest
from tests.integration_tests.utils.parameters import aws_params, \
    reg_setup_params, cls_setup_params


@pytest.mark.skipif(not aws_params.aws_access_key,
                    reason="AWS credentials are not set")
def test_delete_sagemaker_autopilot_endpoint(
        register_language_container, deploy_scripts, setup_database):

    for setup_params in [reg_setup_params, cls_setup_params]:
        _run_test(setup_params, setup_database)


def _run_test(setup_params, db_conn):
    query_deletion = "EXECUTE SCRIPT " \
                     "{schema}.SME_DELETE_SAGEMAKER_AUTOPILOT_ENDPOINT(" \
                     "'{endpoint_name}', '{aws_conn_name}', '{aws_region}')".\
        format(schema=setup_params.schema_name,
               endpoint_name=setup_params.endpoint_name,
               aws_conn_name=aws_params.aws_conn_name,
               aws_region=aws_params.aws_region)

    db_conn.execute(query_deletion)

