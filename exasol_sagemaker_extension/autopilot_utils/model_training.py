import os.path
from sagemaker.automl.automl import AutoML, AutoMLInput


class AutopilotTraining:
    """
    This class is responsible for training a specified Autopilot job
    """

    @staticmethod
    def train(
            job_name: str,
            role: str,
            s3_bucket_uri: str,
            s3_output_path: str,
            target_attribute_name: str,
            problem_type: str = None,
            objective: str = None,
            max_runtime_for_automl_job_in_seconds: int = None,
            max_candidates: int = None,
            max_runtime_per_training_job_in_seconds: int = None):
        unique_model_name = job_name  # model_name = job_name

        s3_train_path = os.path.join(s3_bucket_uri, s3_output_path)
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

        automl_job.fit(
            inputs=s3_input_train, job_name=unique_model_name, wait=False)
        return unique_model_name