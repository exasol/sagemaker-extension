import os


def is_aws_credentials_not_set():
    return not (
            "AWS_ACCESS_KEY_ID" in os.environ and
            "AWS_SECRET_ACCESS_KEY" in os.environ and
            "AWS_DEFAULT_REGION" in os.environ and
            "AWS_ROLE" in os.environ
    )
