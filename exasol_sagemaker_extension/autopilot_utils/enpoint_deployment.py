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

        # arguments of the autopilot deployment method
        kwargs = {
            "initial_instance_count": instance_count,
            "instance_type": instance_type,
            "candidate": self._automl.best_candidate(),
            "wait": True,
            "endpoint_name": endpoint_name
        }

        # add probabilities for classification problem types
        if self.get_endpoint_problem_type() != "Regression":
            kwargs["inference_response_keys"] = \
                ["predicted_label", "probability"]

        self._automl.deploy(**kwargs)
        return endpoint_name

    def get_endpoint_problem_type(self):
        return self._automl_desc['ResolvedAttributes']['ProblemType']
