from collections import namedtuple


POLLING_INTERVAL = 3*60  # seconds
TIMEOUT = 45*60  # seconds


ModelSetupParams = namedtuple("ModelSetupParams", [
    "model_type", "schema_name", "table_name", "target_col",
    "data",  "aws_output_path", "batch_size"])

reg_model_setup_params = ModelSetupParams(
    model_type='reg',
    schema_name="reg_schema",
    table_name="reg_table",
    target_col="output_col",
    data=[f"({i * 1.1}, {i * 1.2}, {i * 10})" for i in range(1, 1000)],
    aws_output_path="reg_path",
    batch_size=10
)

cls_model_setup_params = ModelSetupParams(
    model_type='cls',
    schema_name="cls_schema",
    table_name="cls_table",
    target_col="output_col",
    data=[f"({i * 1.1}, {i * 1.2}, {i % 2})" for i in range(1, 1000)],
    aws_output_path="cls_path",
    batch_size=10
)


def get_aws_params():
    AWSParams = namedtuple("AWSParams", [
        "aws_bucket", "aws_s3_uri", "aws_bucket_uri",  "aws_conn_name"])

    aws_bucket_name = "sme-ci-bucket"
    return AWSParams(
        aws_bucket=aws_bucket_name,
        aws_s3_uri=f"https://{aws_bucket_name}.s3.amazonaws.com",
        aws_bucket_uri=f"s3://{aws_bucket_name}",
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


