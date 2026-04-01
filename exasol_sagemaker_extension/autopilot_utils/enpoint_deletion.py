import boto3


class AutopilotEndpointDeletion:
    """
    This class is responsible for deleting given endpoint.

    note that delete_model() function deletes the deployed models
    (located under "Models" section in Sagemaker web page), not  trained job.
    delete_endpoint() command also delete it, but in order to be sure,
    run delete_model() beforehand.
    """
    @staticmethod
    def delete(endpoint_name: str):
        sm_client = boto3.client("sagemaker")

        endpoint_desc = sm_client.describe_endpoint(EndpointName=endpoint_name)
        config_name = endpoint_desc["EndpointConfigName"]
        config_desc = sm_client.describe_endpoint_config(
            EndpointConfigName=config_name)
        model_names = [
            v["ModelName"] for v in config_desc["ProductionVariants"]]

        sm_client.delete_endpoint(EndpointName=endpoint_name)
        sm_client.delete_endpoint_config(EndpointConfigName=config_name)
        for model_name in model_names:
            sm_client.delete_model(ModelName=model_name)
