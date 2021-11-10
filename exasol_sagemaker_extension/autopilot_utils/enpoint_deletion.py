from sagemaker import Predictor


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
        predictor = Predictor(endpoint_name)
        predictor.delete_model()
        predictor.delete_endpoint()
