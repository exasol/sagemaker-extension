import os

from tests.fixtures.prepare_environment_fixture import CITestEnvironment


class AutopilotTestPolling:
    @staticmethod
    def poll_autopilot_job(job_name, schema_name, ci_test_env: CITestEnvironment) -> str:
        query_polling = "EXECUTE SCRIPT " \
                        "{schema}.SME_POLL_SAGEMAKER_AUTOPILOT_JOB_STATUS(" \
                        "'{job_name}', '{aws_conn_name}', '{aws_region}')". \
            format(schema=schema_name,
                   job_name=job_name,
                   aws_conn_name=ci_test_env.connection_object_for_aws_credentials,
                   aws_region=os.environ["AWS_DEFAULT_REGION"])

        status = ci_test_env.db_conn.execute(query_polling).fetchall()
        return status
