from tests.ci_tests.fixtures.prepare_environment_fixture import CITestEnvironment


class AutopilotTestPrediction:
    @staticmethod
    def predict(endpoint_name, schema_name, ci_test_env: CITestEnvironment) -> list:
        prediction_udf_name = endpoint_name
        query = """SELECT "{schema}"."{udf_name}"(3,4)"""
        query_prediction = query.format(
            schema=schema_name.upper(),
            udf_name=prediction_udf_name)

        prediction = ci_test_env.db_conn.execute(query_prediction).fetchall()
        return prediction
