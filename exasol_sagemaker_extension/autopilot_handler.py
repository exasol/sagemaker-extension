import os.path
from sagemaker import Predictor
from sagemaker.automl.automl import AutoML, AutoMLInput


def train_model(
        model_name: str,
        role: str,
        s3_bucket_uri: str,
        s3_output_path: str,
        target_attribute_name: str,
        problem_type: str = None,
        objective: str = None,
        max_runtime_for_automl_job_in_seconds: int = None,
        max_candidates: int = None,
        max_runtime_per_training_job_in_seconds: int = None):

    unique_model_name = model_name  # model_name = job_name

    s3_train_path = os.path.join(s3_bucket_uri, s3_output_path)
    automl_job = AutoML(
        role=role,
        target_attribute_name=target_attribute_name,
        problem_type=problem_type,
        job_objective=objective,
        total_job_runtime_in_seconds=max_runtime_for_automl_job_in_seconds,
        max_candidates=max_candidates,
        max_runtime_per_training_job_in_seconds=\
                max_runtime_per_training_job_in_seconds
    )

    s3_input_train = AutoMLInput(
        inputs=s3_train_path,
        target_attribute_name=target_attribute_name
    )

    automl_job.fit(
        inputs=s3_input_train, job_name=unique_model_name, wait=False)
    return unique_model_name


def check_training_status(job_name: str):
    automl = AutoML.attach(auto_ml_job_name=job_name)

    describe_response = automl.describe_auto_ml_job()
    return \
        describe_response["AutoMLJobStatus"],\
        describe_response["AutoMLJobSecondaryStatus"]


def deploy_endpoint(
        job_name: str, instance_type: str, instance_count: int):

    unique_endpoint_name = job_name  # endpoint_name = job_name
    automl = AutoML.attach(auto_ml_job_name=job_name)
    best_candidate = automl.describe_auto_ml_job(job_name)["BestCandidate"]
    automl.deploy(
        initial_instance_count=instance_count,
        instance_type=instance_type,
        candidate=best_candidate,
        wait=True,
        endpoint_name=unique_endpoint_name
    )
    return unique_endpoint_name


def delete_endpoint(endpoint_name: str):
    # This function deletes the deployed models (located under "Models" section
    # in Sagemaker web page), not  trained jobs, delete_endpoint() command also
    # delete it, but in order to be sure,  run delete_model() beforehand.

    predictor = Predictor(endpoint_name)
    predictor.delete_model()
    predictor.delete_endpoint()
