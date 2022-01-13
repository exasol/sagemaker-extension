import pytest
from tests.integration_tests.utils.parameters import aws_params, \
    reg_setup_params, cls_setup_params


@pytest.mark.skipif(not aws_params.aws_access_key,
                    reason="AWS credentials are not set")
def test_predict_autopilot_udf(
         deploy_scripts, setup_database):

    problem_types_dict = {
        'regression': {
            'setup_params': reg_setup_params,
            'query': """SELECT "{schema}"."{udf_name}"(1,1)""",
        },
        'classification': {
            'setup_params': cls_setup_params,
            'query': """SELECT "{schema}"."{udf_name}"(3,4)"""
        }
    }

    for _, params in problem_types_dict.items():
        _run_test(
            params['setup_params'], params['query'], setup_database)


def _run_test(setup_params, query, db_conn):
    prediction_udf_name = setup_params.endpoint_name
    query_prediction = query.format(
        schema=setup_params.schema_name.upper(),
        udf_name=prediction_udf_name)

    prediction = db_conn.execute(query_prediction).fetchall()

    print(prediction)
    assert prediction
