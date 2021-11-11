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
-- @param endpoint_name			The name of the Autopilot endpoint
-- @param status				Endpoint status such as 'deployed', 'deleted'
--
function M.update_model_connection_object(endpoint_name, status)
	local conn_name = [[SME_SAGEMAKER_AUTOPILOT_ENDPOINT_CONNECTION_]] .. endpoint_name
	local conn_to = [[TO '{"name":"]] .. endpoint_name .. [[", "status":"]] .. status .. [["}']]
	-- job_name = endpoint_name

	local query = [[CREATE OR REPLACE CONNECTION ]] .. conn_name .. [[ ]] .. conn_to
	local success, result = _G.global_env.pquery(query)
	if not success then
		local error_obj = exaerror.create("",
				'Error occurred in creating model connection object: ' .. result.error_message)
		_G.global_env.error(tostring(error_obj))
	end
end



return M;