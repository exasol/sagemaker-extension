from sagemaker import AutoML


class AutopilotEndpointDeployment:
    """
    This class responsible for deploying an endpoint for a given Autopilot job
    """
    @staticmethod
    def deploy(
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