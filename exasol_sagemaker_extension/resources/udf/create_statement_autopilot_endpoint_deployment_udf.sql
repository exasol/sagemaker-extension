CREATE OR REPLACE PYTHON3_SME SET SCRIPT "SME_AUTOPILOT_ENDPOINT_DEPLOYMENT_UDF"(
    job_name VARCHAR(100),
    endpoint_name VARCHAR(100),
    instance_type VARCHAR(20),
    instance_count INTEGER,
    aws_s3_connection VARCHAR(50),
    aws_region VARCHAR(20)
) EMITS (endpoint_problem_type VARCHAR(32)) AS

from exasol_sagemaker_extension.autopilot_endpoint_deployment_udf import AutopilotEndpointDeploymentUDF
udf = AutopilotEndpointDeploymentUDF(exa)
def run(ctx):
    udf.run(ctx)
/




