---
-- @module autopilot_training_main
--
-- This module exports a given Exasol table into AWS S3.
--

local exaerror = require("exaerror")

_G.global_env = {
    pquery = pquery,
    error = error
}

local required_args = {
	model_name = true,
	input_schema_name = true,
	input_table_or_view_name = true,
	aws_credentials_connection_name = true,
	s3_output_path = true,
	s3_bucket_uri = true,
	iam_sagemaker_role = true,
	target_attribute_name = true,
	problem_type = nil,
	max_runtime_for_automl_job_in_seconds = nil,
	max_runtime_per_training_job_in_seconds = nil,
	max_candidates = nil,
	model_info_schema_name = nil,
	model_info_table_name = nil,
	objective = Nil,
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
		args = {}
		local error_obj = exaerror.create("",
				"Error while parsing input json string, it could not be converted to json object."
		):add_mitigations("Check syntax of the input string json is correct")
		_G.global_env.error(tostring(error_obj))
	end

	if not contains_required_arguments(args) then
		local error_obj = exaerror.create("",
				"Missing required arguments"
		):add_mitigations('Following required arguments have to be specified:' .. concat_required_args())
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

	return args
end


---
-- This is the main function of exporting to S3.
--
-- @param json_str	input parameters as json string
--
--
function main(json_str, exa)
	local aws_s3_handler = require("aws_s3_handler")
	local aws_sagemaker_handler = require("aws_sagemaker_handler")

	local args = parse_arguments(json_str)
	local schema_name = exa.meta.script_schema

	local succ_exporting, res_exporting = aws_s3_handler.export_to_s3(
			args['input_schema_name'],
			args['input_table_or_view_name'],
			args['aws_credentials_connection_name'],
			args['s3_output_path'])
	if not succ_exporting then
		_G.global_env.error('Error occured in exporting Exasol table to AWS S3' .. res_exporting.error_message)
	end


	local succ_training, res_training = aws_sagemaker_handler.autopilot_training(
			schema_name,
			args['model_name'],
			args['aws_credentials_connection_name'],
			args['aws_region'],
			args['iam_sagemaker_role'],
			args['s3_bucket_uri'],
			args['target_attribute_name'],
			args['problem_type'],
			args['objective'],
			args['max_runtime_for_automl_job_in_seconds'],
			args['max_candidates'],
			args['max_runtime_per_training_job_in_seconds'])
	if not succ_training then
		_G.global_env.error('Error occurred in training with Sagemaker Autopilot ' .. res_training.error_message)
	end

	-- TODO save table name into table

end

