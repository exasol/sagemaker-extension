from sagemaker import AutoML


class AutopilotPolling:
    """
    This class is responsible for checking status of a given training job
    """
    @staticmethod
    def check_status(job_name: str):
        automl = AutoML.attach(auto_ml_job_name=job_name)

        describe_response = automl.describe_auto_ml_job()
        return \
            describe_response["AutoMLJobStatus"], \
            describe_response["AutoMLJobSecondaryStatus"]