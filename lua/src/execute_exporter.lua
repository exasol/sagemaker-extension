



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
		_G.global_env.exit()
	end

	if not args['problem_type'] then
		args['problem_type'] = nil
	end

	if not args['max_runtime_for_automl_job_in_seconds'] then
		args['max_runtime_for_automl_job_in_seconds'] = nil
	end

	if not args['max_runtime_per_training_job_in_seconds'] then
		args['max_runtime_per_training_job_in_seconds'] = nil
	end

	if not args['max_candidates'] then
		args['max_candidates'] = nil
	end

	if not args['objective'] then
		args['objective'] = nil
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
function main(json_str)
	local args = parse_arguments(json_str)

	local aws_s3_handler = require("aws_s3_handler")
	local success = aws_s3_handler.export_to_s3(
			args['input_schema_name'],
			args['input_table_or_view_name'],
			args['aws_credentials_connection_name'],
			args['s3_output_path']
	)

	if not success then
		_G.global_env.exit()
	end

end

