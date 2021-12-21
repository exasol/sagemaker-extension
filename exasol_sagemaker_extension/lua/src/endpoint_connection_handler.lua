---
-- @module endpoint_connection_handler
--
-- This module handles operations on EXA connection object
--

local M = {}

local exaerror = require("exaerror")

_G.global_env = {
	pquery = pquery,
	error = error
}


---
--	This function creates or updates an Exasol connection object of a given Autopilot model
--
-- @param aws_s3_connection		The name of the AWS connection object, required to call endpoint in prediction
-- @param aws_region			The name of aws region
-- @param endpoint_name			The name of the Autopilot endpoint
-- @param status				Endpoint status such as 'deployed', 'deleted'
--
function M.update_model_connection_object(aws_s3_connection, aws_region, endpoint_name, status)
	local json = require('cjson')
	local conn_data_dict = {
		aws_s3_connection=aws_s3_connection,
		aws_region = aws_region,
		endpoint_name=endpoint_name,
		status=status,
		batch_size=100
	}

	local conn_name = [[SME_SAGEMAKER_AUTOPILOT_ENDPOINT_CONNECTION_]] .. string.upper(endpoint_name)
	local conn_to = json.encode(conn_data_dict)
	local query = [[CREATE OR REPLACE CONNECTION ]] .. conn_name .. [[ TO ']] .. conn_to .. [[']]

	local success, result = _G.global_env.pquery(query)
	if not success then
		local error_obj = exaerror.create("E-SME-9",
				'Error occurred in creating model connection object: ' .. result.error_message)
		_G.global_env.error(tostring(error_obj))
	end

	return conn_name
end



return M;