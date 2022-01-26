import boto3
import pytest
from tests.ci_tests.utils.autopilot_deletion import AutopilotTestDeletion


def delete_endpoint(endpoint_name, model_setup_params, db_conn):
    print("Delete the created endpoint")
    AutopilotTestDeletion.delete_endpoint(
        endpoint_name, model_setup_params, db_conn)


def delete_s3_bucket():
    print("Delete the created s3 bucket")
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('my-bucket')
    bucket.delete()


def cleanup(func):
    def wrapper(job_name, endpoint_name, model_setup_params, db_conn):
        try:
            return func(job_name, endpoint_name, model_setup_params, db_conn)
        except AssertionError as err:
            print("Error occurred while asserting deployment: %s" % err)
            raise pytest.fail(err)
        except Exception as exc:
            print("Exception occurred while running the test: %s" % exc)
            raise pytest.fail(exc)
        finally:
            delete_endpoint(endpoint_name, model_setup_params, db_conn)
            delete_s3_bucket()

    return wrapper


