import boto3


class AutopilotEndpointDeployment():
    """
    This class responsible for deploying an endpoint for a given Autopilot job
    """

    def __init__(self, job_name: str):
        self._sm_client = boto3.client("sagemaker")
        self._job_desc = self._sm_client.describe_auto_ml_job(
            AutoMLJobName=job_name)

    def deploy(self,
               endpoint_name: str,
               instance_type: str,
               instance_count: int):

        best_candidate = self._job_desc['BestCandidate']

        # deep-enough copy so we can mutate Environment without side effects
        containers = []
        for c in best_candidate['InferenceContainers']:
            container = dict(c)
            container['Environment'] = dict(c.get('Environment', {}))
            containers.append(container)

        # add probabilities for classification problem types
        if self.get_endpoint_problem_type() != "Regression":
            containers[-1]['Environment']['SAGEMAKER_INFERENCE_OUTPUT'] = \
                'predicted_label,probability'

        model_name = best_candidate['CandidateName']
        self._sm_client.create_model(
            ModelName=model_name,
            Containers=containers,
            ExecutionRoleArn=self._job_desc['RoleArn']
        )

        config_name = endpoint_name + '-config'
        self._sm_client.create_endpoint_config(
            EndpointConfigName=config_name,
            ProductionVariants=[{
                'VariantName': 'AllTraffic',
                'ModelName': model_name,
                'InitialInstanceCount': instance_count,
                'InstanceType': instance_type,
            }]
        )

        self._sm_client.create_endpoint(
            EndpointName=endpoint_name,
            EndpointConfigName=config_name
        )

        waiter = self._sm_client.get_waiter('endpoint_in_service')
        waiter.wait(EndpointName=endpoint_name)

        return endpoint_name

    def get_endpoint_problem_type(self):
        return self._job_desc['ResolvedAttributes']['ProblemType']
