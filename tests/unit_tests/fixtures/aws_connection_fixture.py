import os
import pytest


@pytest.fixture(scope="session")
def get_mock_params():
    mock_params = {
        "AWS_AUTOML_JOB_NAME": "test-model-name",
        "AWS_SAGEMAKER_ROLE": "aws_test_role",
        "AWS_KEY_ID": "test_aws_key_id",
        "AWS_ACCESS_KEY": "test_aws_access_key",
        "AWS_REGION": "eu-central-1",
        "AWS_S3_URI": "https://127.0.0.1:4566",
        "AWS_CONNECTION_NAME": "S3_CONNECTION",
        "AWS_BUCKET_URI": "s3://exasol-sagemaker-extension",
        "AWS_OUTPUT_PATH": "train"
    }
    return mock_params


@pytest.fixture(scope="session")
def get_real_params():
    real_params = {
        "AWS_CONNECTION": "AWS_CONNECTION",
        "AWS_REGION": "eu-central-1",
        "AWS_S3_URI": "s3://sagemaker-extension-bucket",
        "AWS_OUTPUT_PATH": "end2end_path",
        "AWS_ROLE": "",
        "AWS_KEY_ID": "",
        "AWS_ACCESS_KEY": "",
        "AWS_SESSION_TOKEN": ""
    }
    os.environ["AWS_SESSION_TOKEN"] = real_params["AWS_SESSION_TOKEN"]
    return real_params