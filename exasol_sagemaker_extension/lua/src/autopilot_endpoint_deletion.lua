---
-- @module autopilot_endpoint_deletion
--
-- This module deletes the deployed Autopilot endpoint
--

local exaerror = require("exaerror")

_G.global_env = {
    pquery = pquery,
    error = error
}

---
-- This function deletes the given Autopilot endpoint
--
-- @schema_name					The name of schema on which the script is deployed
-- @param endpoint_name			The name of the endpoint to be deleted
-- @param aws_s3_connection		The name of the connection object with the AWS credentials
-- @param aws_region			The name of aws region
--
function delete_autopilot_endpoint(schema_name, endpoint_name, aws_s3_connection, aws_region)
	local query = [[SELECT ::schema."SME_AUTOPILOT_ENDPOINT_DELETION_UDF"(
		:endpoint_name,
		:aws_s3_connection,
		:aws_region
	)]]
	local params = {
		schema=schema_name,
		endpoint_name=endpoint_name,
		aws_s3_connection=aws_s3_connection,
		aws_region=aws_region
	}

	local success, result = _G.global_env.pquery(query, params)
	if not success then
		local error_obj = exaerror.create("E-SME-2",
				'Error occurred in deleting Sagemaker endpoint: ' .. result.error_message)
		_G.global_env.error(tostring(error_obj))
	end
end

---
-- This is the main function of Autopilot endpoint deletion
--
-- @param exa					Exa context object
-- @param endpoint_name			The name of the endpoint to be deleted
-- @param aws_s3_connection		The name of the connection object with the AWS credentials
-- @param aws_region			The name of aws region
--
function main(exa, endpoint_name, aws_s3_connection, aws_region)
	local schema_name = exa.meta.script_schema
	delete_autopilot_endpoint(schema_name, endpoint_name, aws_s3_connection, aws_region)

	local exa_conn = require('endpoint_connection_handler')
	exa_conn.update_model_connection_object(
			aws_s3_connection, aws_region, endpoint_name, 'deleted')
end