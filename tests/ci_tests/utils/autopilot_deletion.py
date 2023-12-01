import os
from sagemaker import Predictor

class AutopilotTestDeletion:
    @staticmethod
    def delete_endpoint_via_database(endpoint_name, setup_params, db_conn, aws_conn_name):
        query_deletion = "EXECUTE SCRIPT " \
                         "{schema}.SME_DELETE_SAGEMAKER_AUTOPILOT_ENDPOINT(" \
                         "'{endpoint_name}', '{aws_conn_name}', '{aws_region}')". \
            format(schema=setup_params.schema_name,
                   endpoint_name=endpoint_name,
                   aws_conn_name=aws_conn_name,
                   aws_region=os.environ["AWS_REGION"])

        db_conn.execute(query_deletion)

    @staticmethod
    def delete_endpoint_via_api(endpoint_name):
        predictor = Predictor(endpoint_name)
        predictor.delete_model()
        predictor.delete_endpoint()
