import dataclasses
import os
from inspect import cleandoc
from typing import Optional

import boto3
import pyexasol
import pytest
from click.testing import CliRunner

from exasol_sagemaker_extension.deployment import deploy_cli
from tests.ci_tests.utils.parameters import db_params, \
    reg_model_setup_params, cls_model_setup_params


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
    runner = CliRunner()
    runner.invoke(deploy_cli.main, args_list)


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


@pytest.fixture(scope="session")
def connection_object_for_aws_credentials(db_conn, aws_s3_bucket):
    aws_conn_name = "test_aws_credentials_connection_name"
    aws_region = os.environ["AWS_DEFAULT_REGION"]
    aws_s3_uri = f"https://{aws_s3_bucket}.s3.{aws_region}.amazonaws.com"
    query = "CREATE OR REPLACE  CONNECTION {aws_conn_name} " \
            "TO '{aws_s3_uri}' " \
            "USER '{aws_access_key_id}' IDENTIFIED BY '{aws_secret_access_key}'" \
        .format(aws_conn_name=aws_conn_name,
                aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
                aws_s3_uri=aws_s3_uri)
    db_conn.execute(query)
    print(query)
    yield aws_conn_name
    db_conn.execute(f"DROP CONNECTION {aws_conn_name};")


def _create_aws_s3_bucket():
    s3_client = boto3.client('s3')
    bucket_name = "ci-exasol-sagemaker-extension-bucket"
    try:
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={
                'LocationConstraint': os.environ["AWS_DEFAULT_REGION"]}
        )
    except s3_client.exceptions.BucketAlreadyOwnedByYou as ex:
        print("'BucketAlreadyOwnedByYou' exception is handled")
    return bucket_name


def _remove_aws_s3_bucket_content(bucket_name: str):
    s3_client = boto3.resource('s3')
    bucket = s3_client.Bucket(bucket_name)
    bucket.objects.all().delete()


@pytest.fixture(scope="session")
def aws_s3_bucket():
    bucket_name = _create_aws_s3_bucket()
    yield bucket_name
    _remove_aws_s3_bucket_content(bucket_name)


@pytest.fixture(scope="session")
def aws_sagemaker_role() -> str:
    iam_client = boto3.client('iam')
    role_name = _create_sagemaker_role(iam_client)
    policy_arn = _create_sagemaker_policy(iam_client)
    _attach_policy_to_role(iam_client,
                           policy_arn=policy_arn,
                           role_name=role_name)
    _attach_policy_to_role(iam_client,
                           policy_arn="arn:aws:iam::aws:policy/AmazonSageMakerFullAccess",
                           role_name=role_name)
    return role_name


def _attach_policy_to_role(iam_client, policy_arn, role_name):
    response = iam_client.attach_role_policy(
        PolicyArn=policy_arn,
        RoleName=role_name,
    )


def _create_sagemaker_role(iam_client):
    role_name = "ci-exasol-sagemaker-extension-role"
    try:
        assume_policy_document = cleandoc("""
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "sagemaker.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        """)
        response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=assume_policy_document,
            Description='This role is used for the CI Tests of the exasol.sagemaker-extension',
        )
    except iam_client.exceptions.EntityAlreadyExistsException as ex:
        print("'EntityAlreadyExistsException' exception is handled")
    return role_name


def _create_sagemaker_policy(iam_client) -> str:
    policy_name = "ci-exasol-sagemaker-extension-policy"
    try:
        policy_document = cleandoc("""
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:*"
                    ],
                    "Resource": "*"
                }
            ]
        }
        """)
        response = iam_client.create_policy(
            PolicyName=policy_name,
            PolicyDocument=policy_document,
            Description='This policy is used for the CI Tests of the exasol.sagemaker-extension',

        )
        return response["Policy"]["Arn"]
    except iam_client.exceptions.EntityAlreadyExistsException as ex:
        print("'EntityAlreadyExistsException' exception is handled")
        sts_client = boto3.client('sts')
        account_id = sts_client.get_caller_identity()['Account']
        policy_arn = f'arn:aws:iam::{account_id}:policy/{policy_name}'
        return policy_arn


@dataclasses.dataclass
class CITestEnvironment:
    db_conn: pyexasol.ExaConnection
    aws_s3_bucket: str
    aws_sagemaker_role: str
    connection_object_for_aws_credentials: str
    aws_region: Optional[str] = None

    def __post_init__(self):
        self.aws_region = os.environ["AWS_DEFAULT_REGION"]

    @property
    def aws_bucket_uri(self) -> str:
        aws_bucket_uri = f"s3://{self.aws_s3_bucket}"
        return aws_bucket_uri


@pytest.fixture(scope="session")
def prepare_ci_test_environment(db_conn,
                                aws_s3_bucket,
                                connection_object_for_aws_credentials,
                                aws_sagemaker_role) -> CITestEnvironment:
    _setup_database(db_conn)
    yield CITestEnvironment(db_conn=db_conn,
                            aws_s3_bucket=aws_s3_bucket,
                            connection_object_for_aws_credentials=connection_object_for_aws_credentials,
                            aws_sagemaker_role=aws_sagemaker_role)
