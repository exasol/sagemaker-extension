import os
from exasol_sagemaker_extension import autopilot_handler


class AutopilotTrainingUDF:
    def __init__(self, exa, training_method=autopilot_handler.train_model):
        self.exa = exa
        self.counter = 0
        self.training_method = training_method

    def run(self, ctx):
        aws_s3_connection = ctx.aws_s3_connection
        aws_region = ctx.aws_region  # TODO
        role = ctx.role
        bucket = ctx.bucket
        target_attribute_name = ctx.target_attribute_name
        problem_type = ctx.problem_type
        total_job_runtime_in_seconds = \
            ctx.max_runtime_for_automl_job_in_seconds
        max_candidates = ctx.max_candidates
        max_runtime_per_training_job_in_seconds = \
            ctx.max_runtime_per_training_job_in_seconds

        aws_s3_conn_obj = self.exa.get_connection(aws_s3_connection)

        os.environ["AWS_DEFAULT_REGION"] = aws_region
        os.environ["AWS_ACCESS_KEY_ID"] = aws_s3_conn_obj.user
        os.environ["AWS_SECRET_ACCESS_KEY"] = aws_s3_conn_obj.password

        job_name = self.training_method(
            role=role,
            bucket=bucket,
            target_attribute_name=target_attribute_name,
            problem_type=problem_type,
            max_runtime_for_automl_job_in_seconds=total_job_runtime_in_seconds,
            max_candidates=max_candidates,
            max_runtime_per_training_job_in_seconds= \
                max_runtime_per_training_job_in_seconds
        )

        ctx.emit(job_name)
        self.counter += 1
