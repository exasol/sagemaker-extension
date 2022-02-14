import os

from tests.ci_tests.utils.parameters import aws_params

INSTANCE_TYPE = "ml.c5.large"
INSTANCE_COUNT = 1


class AutopilotTestDeployment:
    @staticmethod
    def deploy_endpoint(job_name, endpoint_name, setup_params, db_conn):
        query_deployment = "EXECUTE SCRIPT " \
                           "{schema}.SME_DEPLOY_SAGEMAKER_AUTOPILOT_ENDPOINT(" \
                           "'{job_name}', '{endpoint_name}', '{schema}', " \
                           "'{instance_type}',  {instance_count}, " \
                           "'{aws_conn_name}', '{aws_region}')". \
            format(schema=setup_params.schema_name,
                   job_name=job_name,
                   endpoint_name=endpoint_name,
                   instance_type=INSTANCE_TYPE,
                   instance_count=INSTANCE_COUNT,
                   aws_conn_name=aws_params.aws_conn_name,
                   aws_region=os.environ["AWS_DEFAULT_REGION"])

        db_conn.execute(query_deployment)
