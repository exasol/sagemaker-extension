from sagemaker import AutoML


class AutopilotEndpointDeployment():
    """
    This class responsible for deploying an endpoint for a given Autopilot job
    """

    def __init__(self, job_name: str):
        self._automl = AutoML.attach(auto_ml_job_name=job_name)
        self._automl_desc = self._automl.describe_auto_ml_job(job_name)

    def deploy(self,
               endpoint_name: str,
               instance_type: str,
               instance_count: int):

        best_candidate = self._automl.best_candidate()
        self._automl .deploy(
            initial_instance_count=instance_count,
            instance_type=instance_type,
            candidate=best_candidate,
            wait=True,
            endpoint_name=endpoint_name
        )

        return endpoint_name

    def get_endpoint_problem_type(self):
        return self._automl_desc['ResolvedAttributes']['ProblemType']
