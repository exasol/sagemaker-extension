import os

from tests.ci_tests.utils.parameters import aws_params


class AutopilotTestPolling:
    @staticmethod
    def poll_autopilot_job(job_name, schema_name, db_conn) -> str:
        query_polling = "EXECUTE SCRIPT " \
                        "{schema}.SME_POLL_SAGEMAKER_AUTOPILOT_JOB_STATUS(" \
                        "'{job_name}', '{aws_conn_name}', '{aws_region}')". \
            format(schema=schema_name,
                   job_name=job_name,
                   aws_conn_name=aws_params.aws_conn_name,
                   aws_region=os.environ["AWS_DEFAULT_REGION"])

        status = db_conn.execute(query_polling).fetchall()
        return status
