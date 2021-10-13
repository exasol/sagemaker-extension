import os
import json
from typing import Callable
from datetime import datetime
from exasol_sagemaker_extension import autopilot_handler


class AutopilotTrainingStatusUDF:
    def __init__(self, exa, check_training_status_method: \
            Callable=autopilot_handler.check_training_status):
        self.exa = exa
        self.counter = 0
        self.check_training_status_method= check_training_status_method

    def run(self, ctx):
        model_name = ctx.model_name
        aws_s3_connection = ctx.aws_s3_connection
        aws_region = ctx.aws_region 

        aws_s3_conn_obj = self.exa.get_connection(aws_s3_connection)
        os.environ["AWS_DEFAULT_REGION"] = aws_region
        os.environ["AWS_ACCESS_KEY_ID"] = aws_s3_conn_obj.user
        os.environ["AWS_SECRET_ACCESS_KEY"] = aws_s3_conn_obj.password

        job_status, job_secondary_status = \
            self.check_training_status_method(model_name)

        ctx.emit(job_status, job_secondary_status)
        self.counter += 1
