---
-- @module autopilot_endpoint_deployment
--
-- This module creates and deploys the best candidate of a trained Autopilot job.
--

local exaerror = require("exaerror")

_G.global_env = {
    pquery = pquery,
    error = error
}

---
-- This function deploys an endpoint for a given Autopilot job
--
-- @schema_name					The name of schema on which the script is deployed
-- @param job_name				Job name of the Autopilot training run
-- @param instance_type			EC2 instance type to deploy this Model to
-- @param instance_count		The initial number of instances to run in endpoint
-- @param aws_s3_connection		The name of the connection object with the AWS credentials
-- @param aws_region			The name of aws region
--
function deploy_autopilot_endpoint(schema_name, job_name, instance_type, instance_count, aws_s3_connection, aws_region)
	local query = [[SELECT ::schema."SME_AUTOPILOT_ENDPOINT_DEPLOYMENT_UDF"(
		:job_name,
		:instance_type,
		:instance_count,
		:aws_s3_connection,
		:aws_region
	)]]
	local params = {
		schema=schema_name,
		job_name=job_name,
		instance_type=instance_type,
		instance_count=instance_count,
		aws_s3_connection=aws_s3_connection,
		aws_region=aws_region
	}

	local success, result = _G.global_env.pquery(query, params)
	if not success then
		local error_obj = exaerror.create("",
				'Error occurred in deploying Sagemaker endpoint: ' .. result.error_message)
		_G.global_env.error(tostring(error_obj))
	end

	return  result[1][1]
end

---
-- This is the main function of deploying Autopilot endpoint
--
-- @param exa					Exa context object
-- @param job_name				Job name of the Autopilot training run
-- @param instance_type			EC2 instance type to deploy this Model to
-- @param instance_count		The initial number of instances to run in endpoint
-- @param aws_s3_connection		the name of the connection object with the AWS credentials
-- @param aws_region			aws region
--
function main(exa, job_name, instance_type, instance_count, aws_s3_connection, aws_region)
	local schema_name = exa.meta.script_schema

	local endpoint_name = deploy_autopilot_endpoint(
			schema_name, job_name, instance_type, instance_count, aws_s3_connection, aws_region)

	local exa_conn = require('endpoint_connection_handler')
	exa_conn.update_model_connection_object(endpoint_name, 'deployed')
	-- TODO: PredictionUDF will be created here in the next PR
end