import pytest
from tests.integration_tests.utils.parameters import aws_params, setup_params


@pytest.mark.skipif(not aws_params.aws_access_key,
                    reason="AWS credentials are not set")
def test_predict_autopilot_udf(
        register_language_container, deploy_scripts, setup_database):
    db_conn = setup_database
    prediction_udf_name = setup_params.endpoint_name

    query_prediction = """SELECT "{schema}"."{udf_name}"(1,1,1,1)""". \
        format(schema=setup_params.schema_name.upper(),
               udf_name=prediction_udf_name)

    prediction = db_conn.execute(query_prediction).fetchall()

    print(prediction)
    assert prediction
