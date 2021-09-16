

---
-- This is the main function of exporting to S3.
--
-- @param json_str	input parameters as json string
--
--

function main(json_str)

	-- manage parameters
	local json = require('cjson')
	local parameters_map = json.decode(json_str)

	if not parameters_map['problem_type'] then
		parameters_map['problem_type'] = 'classification' -- default : 'classification'
	end

	if not parameters_map['max_runtime_for_automl_job_in_seconds'] then
		parameters_map['max_runtime_for_automl_job_in_seconds'] = 1000 -- default : 1000 sec.
	end

	if not parameters_map['max_runtime_per_training_job_in_seconds'] then
		parameters_map['max_runtime_per_training_job_in_seconds'] = 300 -- default : 300 sec.
	end

	if not parameters_map['max_candidates'] then
		parameters_map['max_candidates'] = 50 -- default : 50
	end

	if not parameters_map['objective'] then
		parameters_map['objective'] = 'mean squared error' -- default : 'mean squared error'
	end

	parameters_map['compression_type'] = 'gzip' -- default : 'gzip'


	local aws_s3_handler = require("aws_s3_handler")
	-- import('AWS_S3_HANDLER', 's3_handler')
	aws_s3_handler.export_to_s3(
			parameters_map['input_schema_name']..'.'..parameters_map['input_table_or_view_name'],
			parameters_map['aws_credentials_connection_name'],
			parameters_map['s3_output_path']
	)

end

main(json_str)