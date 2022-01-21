import os
import boto3
import pytest
from collections import namedtuple
from exasol_sagemaker_extension.deployment import deploy_cli
from tests.ci_tests.utils.parameters import db_params, aws_params

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


def __open_schema(db_conn, model_setup):
    query = "CREATE SCHEMA IF NOT EXISTS {schema_name}"
    db_conn.execute(query.format(schema_name=model_setup.schema_name))


def __deploy_scripts(model_setup):
    args_list = [
        "--host", db_params.host,
        "--port", db_params.port,
        "--user", db_params.user,
        "--pass", db_params.password,
        "--schema", model_setup.schema_name
    ]
    deploy_cli.main(args_list)


def __create_tables(db_conn, model_setup):
    query = "CREATE OR REPLACE TABLE {schema_name}.{table_name} " \
            "(col1 FLOAT, col2 FLOAT, output_col INTEGER)". \
        format(schema_name=model_setup.schema_name,
               table_name=model_setup.table_name)
    db_conn.execute(query)


def __insert_into_tables(db_conn, model_setup):
    values = ",".join(model_setup.data)
    query = "INSERT INTO {schema_name}.{table_name} VALUES {values}". \
        format(schema_name=model_setup.schema_name,
               table_name=model_setup.table_name,
               values=values)
    db_conn.execute(query)


def _setup_database(db_conn):
    for model_setup in [reg_model_setup_params, cls_model_setup_params]:
        __open_schema(db_conn, model_setup)
        __deploy_scripts(model_setup)
        __create_tables(db_conn, model_setup)
        __insert_into_tables(db_conn, model_setup)


def _create_aws_connection(conn):
    query = "CREATE OR REPLACE  CONNECTION {aws_conn_name} " \
            "TO '{aws_s3_uri}' " \
            "USER '{aws_key_id}' IDENTIFIED BY '{aws_access_key}'"\
        .format(aws_conn_name=aws_params.aws_conn_name,
                aws_s3_uri=aws_params.aws_s3_uri,
                aws_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                aws_access_key=os.environ["AWS_SECRET_ACCESS_KEY"])
    conn.execute(query)


def _create_aws_s3_bucket():
    s3_client = boto3.client('s3')
    s3_client.create_bucket(
        Bucket=aws_params.aws_bucket,
        region_name=os.environ["AWS_REGION"])


@pytest.fixture(scope="session")
def prepare_ci_test_environment(db_conn):
    _setup_database(db_conn)
    _create_aws_connection(db_conn)
    _create_aws_s3_bucket()
    return db_conn
