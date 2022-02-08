CREATE OR REPLACE PYTHON3_SME SET SCRIPT "SME_AUTOPILOT_ENDPOINT_DELETION_UDF"(
    endpoint_name VARCHAR(100),
    aws_s3_connection VARCHAR(50),
    aws_region VARCHAR(20)
) EMITS (endpoint_name VARCHAR(32)) AS

from exasol_sagemaker_extension.autopilot_endpoint_deletion_udf import AutopilotEndpointDeletionUDF
udf = AutopilotEndpointDeletionUDF(exa)
def run(ctx):
    udf.run(ctx)
/




