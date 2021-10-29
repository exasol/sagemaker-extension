CREATE OR REPLACE PYTHON3_SME SET SCRIPT "SME_AUTOPILOT_JOB_STATUS_POLLING_UDF"(
    job_name VARCHAR(32),
    aws_s3_connection VARCHAR(50),
    aws_region VARCHAR(20)
) EMITS(JobStatus VARCHAR(100), JobSecondaryStatus VARCHAR(100)) AS

from exasol_sagemaker_extension.autopilot_job_status_polling_udf import AutopilotJobStatusPollingUDF
udf = AutopilotJobStatusPollingUDF(exa)
def run(ctx):
    udf.run(ctx)
/