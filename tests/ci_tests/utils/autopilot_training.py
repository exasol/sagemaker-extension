import os
import json
from tests.ci_tests.utils.parameters import reg_model_setup_params, \
    cls_model_setup_params, aws_params


class AutopilotTestTraining:
    def __init__(self, job_name, db_conn):
        self._job_name = job_name
        self._db_conn = db_conn

    @classmethod
    def train_autopilot_regression_job(cls, job_name, db_conn):
        autopilot_regression_trainer = cls(job_name, db_conn)

        problem_params = {
            "problem_type": "Regression",
            "objective": '{"MetricName":"MSE"}'}
        autopilot_regression_trainer.__train(
            reg_model_setup_params,
            problem_params)

    @classmethod
    def train_autopilot_classification_job(cls, job_name, db_conn):
        autopilot_classification_trainer = cls(job_name, db_conn)

        problem_params = {
            "problem_type": "BinaryClassification",
            "objective": '{"MetricName":"F1"}'}
    
        autopilot_classification_trainer.__train(
            cls_model_setup_params,
            problem_params)

    def __train(self, setup_params, problem_params):
        params_dict = {
            "job_name"							: self._job_name,
            "aws_credentials_connection_name"	: aws_params.aws_conn_name,
            "aws_region"						: os.environ["AWS_DEFAULT_REGION"],
            "iam_sagemaker_role"				: os.environ["AWS_ROLE"],
            "s3_bucket_uri"						: aws_params.aws_bucket_uri,
            "s3_output_path"					: setup_params.aws_output_path,
            "input_schema_name"						: setup_params.schema_name,
            "input_table_or_view_name"			: setup_params.table_name,
            "target_attribute_name"				: setup_params.target_col,
            "max_candidates"					: 2,
        }
        params_dict = {**params_dict, **problem_params}

        query_training = \
            "EXECUTE SCRIPT " \
            "{schema}.SME_TRAIN_WITH_SAGEMAKER_AUTOPILOT('{params}')".format(
                schema=setup_params.schema_name, params=json.dumps(params_dict))
        self._db_conn.execute(query_training)
