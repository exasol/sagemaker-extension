---
-- @module aws_sagemaker_handler
--
-- this module handles AWS Sagemaker service operations
--

local M = {}

local exaerror = require("exaerror")

_G.global_env = {
	pquery = pquery,
	error = error
}

---
-- Invoke AWS Sagemaker Autopilot training
--
-- @return result   The name of the Autopilot run job
--
function M.autopilot_training(
        schema_name,
        model_name,
        aws_s3_connection,
        aws_region,
        role,
        s3_bucket_uri,
        s3_output_path,
        target_attribute_name,
        problem_type,
        objective,
        total_job_runtime_in_seconds,
        max_candidates,
        max_runtime_per_training_job_in_seconds)

    local query_training = [[SELECT ::schema.AUTOPILOT_TRAINING_UDF(
        :model_name ,
        :aws_s3_connection ,
        :aws_region ,
        :role ,
        :s3_bucket_uri,
        :s3_output_path,
        :target_attribute_name ,
        :problem_type ,
        :objective ,
        :total_job_runtime_in_seconds ,
        :max_candidates ,
        :max_runtime_per_training_job_in_seconds
        )]]
    local params = {
        schema = schema_name,
        model_name = model_name,
        aws_s3_connection = aws_s3_connection,
        aws_region = aws_region,
        role = role,
        s3_bucket_uri = s3_bucket_uri,
        s3_output_path = s3_output_path,
        target_attribute_name = target_attribute_name,
        problem_type = problem_type,
        objective = objective,
        total_job_runtime_in_seconds = total_job_runtime_in_seconds,
        max_candidates = max_candidates,
        max_runtime_per_training_job_in_seconds = max_runtime_per_training_job_in_seconds
    }

    local success, result = _G.global_env.pquery(query_training, params)
	if not success then
		local error_obj = exaerror.create("",
				'Error occurred in training with Sagemaker Autopilot: ' .. result.error_message)
		_G.global_env.error(tostring(error_obj))
	end

    return result
end

return M;