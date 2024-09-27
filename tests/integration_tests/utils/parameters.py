from collections import namedtuple
import os

'''
This module contains namedtuples that store the necessary parameters for the 
real-case tests. Some tuples like as db_params could have also be used as 
fixtures. However, to avoid the confusion of using some of  parameters as 
fixtures and some as namedtuple, all the necessary params are stored in 
namedtuple rather than fixture.
'''


def get_aws_params():
    AWSParams = namedtuple("AWSParams", [
        "aws_access_key_id", "aws_secret_access_key", "aws_role",
        "aws_region", "aws_s3_uri",  "aws_conn_name"])

    return AWSParams(
        aws_access_key_id="",
        aws_secret_access_key="",
        aws_role="",
        aws_region="eu-central-1",
        aws_s3_uri="https://sagemaker-extension-bucket.s3.amazonaws.com",
        aws_conn_name="aws_connection",
    )


def get_regression_setup_params():
    RegressionSetupParams = namedtuple("RegressionSetupParams", [
        "schema_name", "table_name", "target_col", "data", "aws_output_path",
        "job_name", "endpoint_name", "batch_size"])

    return RegressionSetupParams(
        schema_name="test_in_db_schema",
        table_name="test_reg_table",
        target_col="output_col",
        data=[f"({i * 1.1}, {i * 1.2}, {i * 10})" for i in range(1, 1000)],
        aws_output_path="test_reg_path",
        job_name="regtestjob8",
        endpoint_name="regtestjobendpoint",
        batch_size=10
    )


def get_classification_setup_params():
    ClassificationSetupParams = namedtuple("ClassificationSetupParams", [
        "schema_name", "table_name", "target_col", "data", "aws_output_path",
        "job_name", "endpoint_name", "batch_size"])

    return ClassificationSetupParams(
        schema_name="test_in_db_schema",
        table_name="test_cls_table",
        target_col="output_col",
        data=[f"({i * 1.1}, {i * 1.2}, {i % 2})" for i in range(1, 1000)],
        aws_output_path="test_cls_path",
        job_name="clstestjob8",
        endpoint_name="clstestjobendpoint",
        batch_size=10
    )


aws_params = get_aws_params()
reg_setup_params = get_regression_setup_params()
cls_setup_params = get_classification_setup_params()
