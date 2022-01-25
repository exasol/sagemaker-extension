
class AutopilotTestPrediction:
    @staticmethod
    def predict(endpoint_name, schema_name, db_conn) -> list:
        prediction_udf_name = endpoint_name
        query = """SELECT "{schema}"."{udf_name}"(3,4)"""
        query_prediction = query.format(
            schema=schema_name.upper(),
            udf_name=prediction_udf_name)

        prediction = db_conn.execute(query_prediction).fetchall()

        print(prediction)
        return prediction
