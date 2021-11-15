---
-- @module install_autopilot_prediction_udf
--
-- This module generates and deploys Autopilot prediction udf
--

local M = {}

local exaerror = require("exaerror")

_G.global_env = {
	pquery = pquery,
	error = error
}

---
-- Split the given string using the specified seperator into a list of strings
--
-- @param character		The separator to use when splitting the string.
--
-- @return  a list of strings
--
function string:split(seperator)
  local splitted_result = {}
  local i = 1
  for str in string.gmatch(self, "[^"..seperator.."]+") do
    splitted_result[i] = str
    i = i + 1
  end
  return splitted_result
end

---
-- Generate and deploy prediction udf
--
-- @param schema		       	The name of schema where the prediction udf gets created
-- @param endpoint_name     	The name of endpoint is for which prediction UDF is created
-- @param model_conn_name   	The name of connection holds information about mode
-- @param input_params          Input parameters for the prediction udf
-- @param output_params			Output for the prediction udf
--
function M.install_udf(schema, endpoint_name, model_conn_name, input_params, output_params)
    local query_create  =
	"CREATE OR REPLACE PYTHON3_SME SET SCRIPT "
		.. schema .. ".\"ENDPOINT_PREDICTION_" .. endpoint_name .. "_UDF\""
		.. "(" .. table.concat(input_params, ',') .. ")"
		.. "EMITS (" .. table.concat(output_params, ',') .. ") AS\n"
	.. "from exasol_sagemaker_extension.autopilot_prediction import AutopilotPredictionUDF\n"
	.. "udf = AutopilotPredictionUDF(exa, '" .. model_conn_name .. "')\ndef run(ctx):\n\tudf.run(ctx)\n/"

    local success, result = _G.global_env.pquery(query_create)
	if not success then
		local error_obj = exaerror.create("",
				'Error occurred in installing prediction udf: ' .. result.error_message)
		_G.global_env.error(tostring(error_obj))
	end
end

---
-- This function parses the given metadata into parameters for the prediction udf
--
-- @param metadata_row		A row of metadata table
--
-- @return  input and output params of the prediction udf
--
function M.parse_metadata(metadata_row)
	local target_column = metadata_row[1][1]
	local col_names_list = metadata_row[1][2]:split(';')
	local col_types_list = metadata_row[1][3]:split(';')

	local input_params = {}
	local output_params = {}
	local target_param = nil
	for i=1, #col_names_list do
		if col_names_list[i] ~= target_column then
			input_params[#input_params+1]=col_names_list[i] .. ' ' .. col_types_list[i]
			output_params[#output_params+1]=col_names_list[i] .. ' ' .. col_types_list[i]
		else
			target_param = col_names_list[i] .. ' ' .. col_types_list[i]
		end
	end
	output_params[#output_params+1] = target_param

	return input_params, output_params
end

---
-- This is the main function of installing Prediction UDF
--
-- @param job_name          	The name of the job, is used to find out the metadata
-- @param script_schema_name	The name of schema in which metadata table is stored
-- @param endpoint_name     	The name of endpoint is for which prediction UDF is created
-- @param schema_name       	The name of schema where PredictionUDF gets created
-- @param model_conn_name   	The name of connection holds information about model
--
function M.main(job_name, script_schema_name, endpoint_name, schema_name, model_conn_name)
    local db_metadata_reader = require('db_metadata_reader')
    local metadata_row = db_metadata_reader.read_metadata(
            script_schema_name, job_name,
			{'TARGET_ATTRIBUTE_NAME', 'COLUMN_NAMES', 'COLUMN_TYPES'})

    local input_params, output_params = M.parse_metadata(metadata_row)

	M.install_udf(schema_name, endpoint_name, model_conn_name, input_params, output_params)

end

return M;