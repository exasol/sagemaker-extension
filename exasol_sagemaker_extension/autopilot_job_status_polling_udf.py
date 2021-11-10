import os
from typing import Callable
from exasol_sagemaker_extension.autopilot_utils.status_polling import \
    AutopilotPolling


class AutopilotJobStatusPollingUDF:
    def __init__(self, exa,
                 check_status_method: Callable= AutopilotPolling.check_status):
        self.exa = exa
        self.counter = 0
        self.check_status_method = check_status_method

    def run(self, ctx):
        job_name = ctx.job_name
        aws_s3_connection = ctx.aws_s3_connection
        aws_region = ctx.aws_region 

        aws_s3_conn_obj = self.exa.get_connection(aws_s3_connection)
        os.environ["AWS_DEFAULT_REGION"] = aws_region
        os.environ["AWS_ACCESS_KEY_ID"] = aws_s3_conn_obj.user
        os.environ["AWS_SECRET_ACCESS_KEY"] = aws_s3_conn_obj.password

        job_status, job_secondary_status = self.check_status_method(job_name)

        ctx.emit(job_status, job_secondary_status)
        self.counter += 1
