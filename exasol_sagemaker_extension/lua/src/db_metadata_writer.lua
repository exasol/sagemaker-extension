---
-- @module db_metadata_writer
--
-- This module inserts the metadata of an Autopilot job
--

local M = {}

local exaerror = require("exaerror")

_G.global_env = {
	pquery = pquery,
	error = error
}

---
-- Insert the metadata of an Autopilot job
--
function M.insert_metadata_into_db(
			schema_name,
			job_name,
			aws_credentials_connection_name,
			iam_sagemaker_role,
			s3_bucket_uri,
			s3_output_path,
			target_attribute_name,
			problem_type,
			objective,
			max_runtime_for_automl_job_in_seconds,
			max_candidates,
			max_runtime_per_training_job_in_seconds,
			session_id,
			script_user,
			col_names,
			col_types
)
	local query_inserting = [[INSERT INTO ::schema."SME_METADATA_AUTOPILOT_JOBS" VALUES(
			CURRENT_TIMESTAMP,
			:job_name,
			:aws_credentials_connection_name,
			:iam_sagemaker_role,
			:s3_bucket_uri,
			:s3_output_path,
			:target_attribute_name,
			:problem_type,
			:objective,
			:max_runtime_for_automl_job_in_seconds,
			:max_candidates,
			:max_runtime_per_training_job_in_seconds,
			:session_id,
			:script_user,
			:col_names,
			:col_types
        )]]
    local params = {
        schema = schema_name,
		job_name=job_name,
		aws_credentials_connection_name=aws_credentials_connection_name,
		iam_sagemaker_role=iam_sagemaker_role,
		s3_bucket_uri=s3_bucket_uri,
		s3_output_path=s3_output_path,
		target_attribute_name=target_attribute_name,
		problem_type=problem_type,
		objective=objective,
		max_runtime_for_automl_job_in_seconds=max_runtime_for_automl_job_in_seconds,
		max_candidates=max_candidates,
		max_runtime_per_training_job_in_seconds=max_runtime_per_training_job_in_seconds,
		session_id=session_id,
		script_user=script_user,
		col_names=col_names,
		col_types=col_types
    }

	local success, result = _G.global_env.pquery(query_inserting, params)
	if not success then
		local error_obj = exaerror.create("E-SME-8",
				'Error occurred in inserting metadata into database: ' .. result.error_message)
		_G.global_env.error(tostring(error_obj))
	end
end

return M;

