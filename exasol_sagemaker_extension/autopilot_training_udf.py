import os
import json
from typing import Callable
from datetime import datetime

from exasol_sagemaker_extension import autopilot_handler


class AutopilotTrainingUDF:
    def __init__(self, exa,
                 training_method: Callable = autopilot_handler.train_model):
        self.exa = exa
        self.counter = 0
        self.training_method = training_method

    def run(self, ctx):
        model_name = ctx.model_name
        aws_s3_connection = ctx.aws_s3_connection
        aws_region = ctx.aws_region  # TODO
        role = ctx.role
        s3_bucket_uri = ctx.s3_bucket_uri
        s3_output_path = ctx.s3_output_path
        target_attribute_name = ctx.target_attribute_name
        problem_type = ctx.problem_type
        objective = ctx.objective
        total_job_runtime_in_seconds = \
            ctx.max_runtime_for_automl_job_in_seconds
        max_candidates = ctx.max_candidates
        max_runtime_per_training_job_in_seconds = \
            ctx.max_runtime_per_training_job_in_seconds

        unique_model_name = '-'.join(
            (model_name, datetime.utcnow().strftime("%d%b%y-%H%M")))

        if objective:  # <dict> required, eg. '{"MetricName": "Accuracy"}'
            objective = json.loads(objective)

        aws_s3_conn_obj = self.exa.get_connection(aws_s3_connection)
        os.environ["AWS_DEFAULT_REGION"] = aws_region
        os.environ["AWS_ACCESS_KEY_ID"] = aws_s3_conn_obj.user
        os.environ["AWS_SECRET_ACCESS_KEY"] = aws_s3_conn_obj.password

        job_name = self.training_method(
            model_name=unique_model_name,
            role=role,
            s3_bucket_uri=s3_bucket_uri,
            s3_output_path=s3_output_path,
            target_attribute_name=target_attribute_name,
            problem_type=problem_type,
            objective=objective,
            max_runtime_for_automl_job_in_seconds=total_job_runtime_in_seconds,
            max_candidates=max_candidates,
            max_runtime_per_training_job_in_seconds= \
                max_runtime_per_training_job_in_seconds
        )

        ctx.emit(job_name)
        self.counter += 1
