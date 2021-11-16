from collections import namedtuple


def get_aws_params():
    AWSParams = namedtuple("AWSParams", [
        "aws_key_id", "aws_access_key", "aws_role",
        "aws_region", "aws_s3_uri", "aws_output_path"])

    return AWSParams(
        aws_key_id="",
        aws_access_key="",
        aws_role="",
        aws_region="eu-central-1",
        aws_s3_uri="https://sagemaker-extension-bucket.s3.amazonaws.com",
        aws_output_path="test_path"
    )


def get_db_params():
    DBParams = namedtuple("DBParams", [
        "host", "port", "user", "password"])

    return DBParams(
        host="127.0.0.1",
        port="9563",
        user="sys",
        password="exasol"
    )


def get_setup_params():
    SetupParams = namedtuple("SetupParams", [
        "schema_name", "table_name", "target_col", "data",
        "aws_conn_name", "job_name", "endpoint_name"])

    return SetupParams(
        schema_name="test_in_db_schema",
        table_name="test_table",
        target_col="output_col",
        data=[f"({i * 1.1}, {i * 1.2}, {i * 10})" for i in range(1, 1000)],
        aws_conn_name="aws_connection",
        job_name="testjob5",
        endpoint_name="testjob5endpoint"
    )


aws_params = get_aws_params()
db_params = get_db_params()
setup_params = get_setup_params()
