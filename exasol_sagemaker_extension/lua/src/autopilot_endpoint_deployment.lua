---
-- @module autopilot_endpoint_deployment
--
-- This module creates and deploys the best candidate of a trained Autopilot job.
--

local exaerror = require("exaerror")
local validate_input = require("validate_input")

_G.global_env = {
    pquery = pquery,
    error = error
}

---
-- This function deploys an endpoint for a given Autopilot job
--
-- @schema_name					The name of schema on which the script is deployed
-- @param job_name				Job name of the Autopilot training run
-- @param endpoint_name			The name of endpoint to be created and deployed
-- @param instance_type			EC2 instance type to deploy this Model to
-- @param instance_count		The initial number of instances to run in endpoint
-- @param aws_s3_connection		The name of the connection object with the AWS credentials
-- @param aws_region			The name of aws region
--
function deploy_autopilot_endpoint(
		script_schema_name, job_name, endpoint_name,
		instance_type, instance_count, aws_s3_connection, aws_region)
	local query = [[SELECT ::schema."SME_AUTOPILOT_ENDPOINT_DEPLOYMENT_UDF"(
		:job_name,
		:endpoint_name,
		:instance_type,
		:instance_count,
		:aws_s3_connection,
		:aws_region
	)]]
	local params = {
		schema=script_schema_name,
		job_name=job_name,
		endpoint_name=endpoint_name,
		instance_type=instance_type,
		instance_count=instance_count,
		aws_s3_connection=aws_s3_connection,
		aws_region=aws_region
	}

	local success, result = _G.global_env.pquery(query, params)
	if not success then
		local error_obj = exaerror.create("E-SME-3",
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
-- @param endpoint_name			The name of endpoint to be created and deployed. It is also the name of the UDF to be created.
-- @param schema_name			The name of schema where PredictionUDF gets created
-- @param instance_type			EC2 instance type to deploy this Model to
-- @param instance_count		The initial number of instances to run in endpoint
-- @param aws_s3_connection		The name of the connection object with the AWS credentials
-- @param aws_region			The name of aws region
--
function main(
		exa, job_name, endpoint_name, schema_name,
		instance_type, instance_count, aws_s3_connection, aws_region)
	local script_schema_name = exa.meta.script_schema

	if not validate_input.is_autopilot_endpoint_name_valid(endpoint_name) then
		local error_obj = exaerror.create("E-SME-11",
				"Invalid endpoint name " ..job_name
		):add_mitigations("The name of endpoint should match the following pattern: ^[a-zA-Z0-9]{0,62}")
		_G.global_env.error(tostring(error_obj))
	end

	local endpoint_problem_type = deploy_autopilot_endpoint(
			script_schema_name, job_name, endpoint_name, instance_type,
			instance_count, aws_s3_connection, aws_region)

	local endpoint_conn = require('endpoint_connection_handler')
	local model_conn_name = endpoint_conn.update_model_connection_object(
			aws_s3_connection, aws_region, endpoint_name, 'deployed')

	local install_prediction_udf = require('install_autopilot_prediction_udf')
	install_prediction_udf.main(job_name, endpoint_problem_type,
			script_schema_name, endpoint_name, schema_name, model_conn_name)
end