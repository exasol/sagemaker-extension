CREATE OR REPLACE PYTHON3_SME SET SCRIPT "SME_AUTOPILOT_TRAINING_UDF"(
    job_name VARCHAR(23),
    aws_s3_connection VARCHAR(50),
    aws_region VARCHAR(20),
    role VARCHAR(200),
    s3_bucket_uri VARCHAR(200),
    s3_output_path VARCHAR(200),
    target_attribute_name VARCHAR(200),
    problem_type VARCHAR(100),
    objective VARCHAR(100),
    max_runtime_for_automl_job_in_seconds INTEGER,
    max_candidates INTEGER,
    max_runtime_per_training_job_in_seconds INTEGER
) EMITS (job_name VARCHAR(32)) AS

from exasol_sagemaker_extension.autopilot_training_udf import AutopilotTrainingUDF
udf = AutopilotTrainingUDF(exa)
def run(ctx):
    udf.run(ctx)
/




