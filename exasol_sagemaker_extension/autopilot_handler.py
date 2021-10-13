from sagemaker.automl.automl import AutoML, AutoMLInput
from datetime import datetime


def train_model(
        role: str,
        bucket: str,
        target_attribute_name: str,
        problem_type: str = None,
        objective: str = None,
        max_runtime_for_automl_job_in_seconds: int = None,
        max_candidates: int = None,
        max_runtime_per_training_job_in_seconds: int = None
):
    job_name = '-'.join(('train', datetime.now().strftime("%Y-%m-%d-%H-%M-%S")))
    s3_train_path = 's3://{}/train'.format(bucket)

    automl_job = AutoML(
        role=role,
        target_attribute_name=target_attribute_name,
        problem_type=problem_type,
        job_objective=objective,
        total_job_runtime_in_seconds=max_runtime_for_automl_job_in_seconds,
        max_candidates=max_candidates,
        max_runtime_per_training_job_in_seconds= \
                max_runtime_per_training_job_in_seconds
    )

    s3_input_train = AutoMLInput(
        inputs=s3_train_path,
        target_attribute_name=target_attribute_name
    )

    automl_job.fit(inputs=s3_input_train, job_name=job_name, wait=False)
    return job_name



