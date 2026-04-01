import boto3


class AutopilotPolling:
    """
    This class is responsible for checking status of a given training job
    """
    @staticmethod
    def check_status(job_name: str):
        sm_client = boto3.client("sagemaker")

        describe_response = sm_client.describe_auto_ml_job(
            AutoMLJobName=job_name)
        return \
            describe_response["AutoMLJobStatus"], \
            describe_response["AutoMLJobSecondaryStatus"]