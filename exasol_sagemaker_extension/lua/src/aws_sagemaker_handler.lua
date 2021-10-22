---
-- @module aws_sagemaker_handler
--
-- this module handles AWS Sagemaker service operations
--

local M = {}

---
-- Invoke AWS Sagemaker Autopilot training
--
-- @return boolean indicating whether it is exported successfully
--
function M.autopilot_training(
        model_name,
        aws_s3_connection,
        aws_region,
        role,
        bucket,
        target_attribute_name,
        problem_type,
        objective,
        total_job_runtime_in_seconds,
        max_candidates,
        max_runtime_per_training_job_in_seconds)

    local query_training = [[SELECT ::schema.AUTOPILOTTRAININGUDF(
        :model_name ,
        :aws_s3_connection ,
        :aws_region ,
        :role ,
        :bucket ,
        :target_attribute_name ,
        :problem_type ,
        :objective ,
        :total_job_runtime_in_seconds ,
        :max_candidates ,
        :max_runtime_per_training_job_in_seconds
        )]]
    local params = {
        model_name = model_name,
        aws_s3_connection = aws_s3_connection,
        aws_region = aws_region,
        role = role,
        bucket = bucket,
        target_attribute_name = target_attribute_name,
        problem_type = problem_type,
        objective = objective,
        total_job_runtime_in_seconds = total_job_runtime_in_seconds,
        max_candidates = max_candidates,
        max_runtime_per_training_job_in_seconds = max_runtime_per_training_job_in_seconds
    }

    local success, result = _G.global_env.pquery(query_training, params)
    return success, result
end

return M;