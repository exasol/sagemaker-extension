---
-- @module autopilot_job_status_polling
--
-- This module polls Autopilot job status and saves is if need
--

local exaerror = require("exaerror")

_G.global_env = {
    pquery = pquery,
    error = error
}

---
-- This function returns Autopilot training job status
--
-- @param exa					Exa context object
-- @param job_name				Job name of the Autopilot training run
-- @param aws_s3_connection		the name of the connection object with the AWS credentials
-- @param aws_region			aws region
--
function poll_autopilot_job_status(schema_name, job_name, aws_s3_connection, aws_region)
	local query = [[SELECT ::schema."SME_AUTOPILOT_JOB_STATUS_POLLING_UDF"(
		:job_name,
		:aws_s3_connection,
		:aws_region
	)]]
	local params = {
		schema=schema_name,
		job_name=job_name,
		aws_s3_connection=aws_s3_connection,
		aws_region=aws_region
	}
	local success, result = _G.global_env.pquery(query, params)
	if not success then
		local error_obj = exaerror.create("E-SME-4",
				'Error occurred in polling Sagemaker Autopilot job status: ' .. result.error_message)
		_G.global_env.error(tostring(error_obj))
	end

	local summary = {}
	summary[#summary + 1] = {result[1][1], result[1][2]}
	return  summary, "Job_Status varchar(100), Job_Secondary_Status varchar(100)"
end


---
-- This is the main function of polling Autopilot training
--
-- @param exa					Exa context object
-- @param job_name				Job name of the Autopilot training run
-- @param aws_s3_connection		the name of the connection object with the AWS credentials
-- @param aws_region			aws region
--
function main(exa, job_name, aws_s3_connection, aws_region)
	local schema_name = exa.meta.script_schema
	return poll_autopilot_job_status(
			schema_name, job_name, aws_s3_connection, aws_region)

	-- TODO optionally save into table
end