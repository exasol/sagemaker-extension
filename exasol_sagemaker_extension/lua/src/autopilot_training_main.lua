---
-- @module autopilot_training_main
--
-- This module exports a given Exasol table into AWS S3.
--

local exaerror = require("exaerror")
local validate_input = require("validate_input")

_G.global_env = {
    pquery = pquery,
    error = error
}

local required_args = {
	job_name = true,
	input_schema_name = true,
	input_table_or_view_name = true,
	aws_credentials_connection_name = true,
	s3_bucket_uri = true,
	s3_output_path = true,
	iam_sagemaker_role = true,
	target_attribute_name = true,
	problem_type = nil,
	max_runtime_for_automl_job_in_seconds = nil,
	max_runtime_per_training_job_in_seconds = nil,
	max_candidates = nil,
	model_info_schema_name = nil,
	model_info_table_name = nil,
	objective = nil,
	aws_tags = nil
}

---
-- Returns concatenated string of the  required arguments
--
-- @return concatenated string
--
function concat_required_args()
    local concat_args = ''
    for arg, is_required in pairs(required_args) do
        if is_required then
            concat_args = concat_args .. "\n" .. arg
        end
    end
    return concat_args
end

---
-- Checks whether the list of required arguments is subset of the user specified argument list
--
-- @param args	a table including arguments keys and their values
--
-- @return boolean, true if the user specified arguments contain all required arguments
--
function contains_required_arguments(args)
   for arg, is_required in pairs(required_args) do
      if is_required and not args[arg] then
         return false
      end
    end
   return true
end


---
-- Parse a given arguments in json string format.
--
-- @param json_str	input parameters as json string
--
-- @return lua table including parameters
--
function parse_arguments(json_str)
	local json = require('cjson')
	local success, args =  pcall(json.decode, json_str)
	if not success then
		local error_obj = exaerror.create("E-SME-5",
				"Error while parsing input json string, it could not be converted to json object:"
		):add_mitigations("Check syntax of the input string json is correct")
		_G.global_env.error(tostring(error_obj))
	end

	if not contains_required_arguments(args) then
		local error_obj = exaerror.create("E-SME-6", "Missing required arguments"
		):add_mitigations('Following required arguments have to be specified: ' .. concat_required_args())
		_G.global_env.error(tostring(error_obj))
	end

	if not validate_input.is_autopilot_job_name_valid(args['job_name']) then
		local error_obj = exaerror.create("E-SME-11",
				"Invalid job name " .. args['job_name']
		):add_mitigations("The name of job should match the following pattern: ^[a-zA-Z0-9]{0,31}")
		_G.global_env.error(tostring(error_obj))
	end

	if not args['problem_type'] then
		args['problem_type'] = NULL
	end

	if not args['max_runtime_for_automl_job_in_seconds'] then
		args['max_runtime_for_automl_job_in_seconds'] = NULL
	end

	if not args['max_runtime_per_training_job_in_seconds'] then
		args['max_runtime_per_training_job_in_seconds'] = NULL
	end

	if not args['max_candidates'] then
		args['max_candidates'] = NULL
	end

	if not args['objective'] then
		args['objective'] = NULL
	end

	args['compression_type'] = 'gzip' -- default : 'gzip'

	-- store following params as uppercase
	args["input_schema_name"] = string.upper(args["input_schema_name"])
	args["input_table_or_view_name"] = string.upper(args["input_table_or_view_name"])
	args["target_attribute_name"] = string.upper(args["target_attribute_name"])

	return args
end


---
-- This function invokes export_to_s3 method in aws_s3_handler module
--
-- @param args		A table including input parameters
--
function export_to_s3_caller(args)
	local aws_s3_handler = require("aws_s3_handler")
	aws_s3_handler.export_to_s3(
			args['input_schema_name'],
			args['input_table_or_view_name'],
			args['aws_credentials_connection_name'],
			args['s3_output_path'])
end

---
-- This function invokes autopilot_training in aws_sagemaker_handler module
--
-- @param exa			Exa context
-- @param arg			A table including input parameters
--
-- @return job_name		Job name of the Autopilot training run
--
function train_autopilot_caller(exa, args)
	local schema_name = exa.meta.script_schema
	local aws_sagemaker_handler = require("aws_sagemaker_handler")
	local job_name = aws_sagemaker_handler.train_autopilot(
		schema_name,
		args['job_name'],
		args['aws_credentials_connection_name'],
		args['aws_region'],
		args['iam_sagemaker_role'],
		args['s3_bucket_uri'],
		args['s3_output_path'],
		args['target_attribute_name'],
		args['problem_type'],
		args['objective'],
		args['max_runtime_for_automl_job_in_seconds'],
		args['max_candidates'],
		args['max_runtime_per_training_job_in_seconds'])

	return job_name
end

---
-- This method returns names and types of columns as comma-separated strings respectively.
--
-- @param schema_name		The name of schema where the table is in.
-- @param table_name		The name of table from which column information is retrieved.
--
-- return two strings including column names and types
--
function get_table_columns(schema_name, table_name)
	local query = [[SELECT COLUMN_NAME , COLUMN_TYPE FROM SYS.EXA_ALL_COLUMNS eac
					WHERE COLUMN_SCHEMA = :schema_name AND COLUMN_TABLE = :table_name]]
	local params = {schema_name=schema_name, table_name=table_name}

	local success, res = _G.global_env.pquery(query, params)
	if not success then
		local error_obj = exaerror.create("F-SME-2",
				"Error while getting columns information from SYS.EXA_ALL_COLUMNS: " ..  res.error_message)
		_G.global_env.error(tostring(error_obj))
	end

	local col_names, col_types = {}, {}
	for i=1, #res do
		col_names[#col_names+1] = res[i][1]
		col_types[#col_types+1] = res[i][2]
	end
	return table.concat(col_names, ';'), table.concat(col_types, ';')

end

---
-- This method saves the metdata of the job running for training in Autopilot to Database
--
-- @param exa			Exa context
-- @param args			A table including input parameters
-- @param job_name		The name of the Autopilot job
--
function insert_metadata_into_db_caller(exa, args, job_name)
	local schema_name = exa.meta.script_schema
	local col_names, col_types = get_table_columns(
			args['input_schema_name'], args['input_table_or_view_name'])

	local db_metadata_writer = require("db_metadata_writer")
	db_metadata_writer.insert_metadata_into_db(
			schema_name,
			job_name,
			args['aws_credentials_connection_name'],
			args['iam_sagemaker_role'],
			args['s3_bucket_uri'],
			args['s3_output_path'],
			args['target_attribute_name'],
			args['problem_type'],
			args['objective'],
			args['max_runtime_for_automl_job_in_seconds'],
			args['max_candidates'],
			args['max_runtime_per_training_job_in_seconds'],
			exa.meta.session_id,
			exa.meta.current_user,
			col_names,
			col_types
	)
end

---
-- This is the main function of exporting to S3.
--
-- @param json_str	input parameters as json string
--
function main(json_str, exa)
	local args = parse_arguments(json_str)
	export_to_s3_caller(args)
	local job_name = train_autopilot_caller(exa, args)
	insert_metadata_into_db_caller(exa, args, job_name)

end

