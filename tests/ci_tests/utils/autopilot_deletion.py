import os
from tests.ci_tests.utils.parameters import aws_params


class AutopilotTestDeletion:
    @staticmethod
    def delete_endpoint(endpoint_name, setup_params, db_conn):
        query_deletion = "EXECUTE SCRIPT " \
                         "{schema}.SME_DELETE_SAGEMAKER_AUTOPILOT_ENDPOINT(" \
                         "'{endpoint_name}', '{aws_conn_name}', '{aws_region}')". \
            format(schema=setup_params.schema_name,
                   endpoint_name=endpoint_name,
                   aws_conn_name=aws_params.aws_conn_name,
                   aws_region=os.environ["AWS_REGION"])

        db_conn.execute(query_deletion)
