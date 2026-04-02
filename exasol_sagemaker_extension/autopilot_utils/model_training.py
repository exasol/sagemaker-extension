import os.path
import boto3


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
            objective: dict | None = None,
            max_runtime_for_automl_job_in_seconds: int = None,
            max_candidates: int = None,
            max_runtime_per_training_job_in_seconds: int = None):
        unique_model_name = job_name  # model_name = job_name

        s3_train_path = os.path.join(s3_bucket_uri, s3_output_path)

        automl_config = {
            "AutoMLJobName": unique_model_name,
            "InputDataConfig": [{
                "DataSource": {
                    "S3DataSource": {
                        "S3DataType": "S3Prefix",
                        "S3Uri": s3_train_path,
                    }
                },
                "TargetAttributeName": target_attribute_name,
            }],
            "OutputDataConfig": {
                "S3OutputPath": s3_train_path,
            },
            "RoleArn": role,
        }

        auto_ml_job_config = {}
        if max_runtime_for_automl_job_in_seconds is not None:
            auto_ml_job_config["CompletionCriteria"] = {
                "MaxAutoMLJobRuntimeInSeconds":
                    max_runtime_for_automl_job_in_seconds,
            }
        if max_candidates is not None:
            auto_ml_job_config.setdefault("CompletionCriteria", {})[
                "MaxCandidates"] = max_candidates
        if max_runtime_per_training_job_in_seconds is not None:
            auto_ml_job_config.setdefault("CompletionCriteria", {})[
                "MaxRuntimePerTrainingJobInSeconds"] = \
                max_runtime_per_training_job_in_seconds
        if auto_ml_job_config:
            automl_config["AutoMLJobConfig"] = auto_ml_job_config

        if problem_type is not None:
            automl_config["ProblemType"] = problem_type
        if objective is not None:
            automl_config["AutoMLJobObjective"] = objective

        sm_client = boto3.client("sagemaker")
        sm_client.create_auto_ml_job(**automl_config)

        return unique_model_name