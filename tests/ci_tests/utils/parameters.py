from collections import namedtuple


def get_aws_params():
    AWSParams = namedtuple("AWSParams", [
        "aws_bucket", "aws_s3_uri",  "aws_conn_name"])

    aws_bucket_name = "sme-ci-bucket"
    return AWSParams(
        aws_bucket=aws_bucket_name,
        aws_s3_uri=f"https://{aws_bucket_name}.s3.amazonaws.com",
        aws_conn_name="aws_connection",
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


aws_params = get_aws_params()
db_params = get_db_params()


