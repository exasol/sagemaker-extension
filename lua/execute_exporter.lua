

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
		parameters_map['problem_type'] = nil
	end

	if not parameters_map['max_runtime_for_automl_job_in_seconds'] then
		parameters_map['max_runtime_for_automl_job_in_seconds'] = nil
	end

	if not parameters_map['max_runtime_per_training_job_in_seconds'] then
		parameters_map['max_runtime_per_training_job_in_seconds'] = nil
	end

	if not parameters_map['max_candidates'] then
		parameters_map['max_candidates'] = nil
	end

	if not parameters_map['objective'] then
		parameters_map['objective'] = nil
	end

	parameters_map['compression_type'] = 'gzip' -- default : 'gzip'


	local aws_s3_handler = require("aws_s3_handler").init(pquery)
	aws_s3_handler.export_to_s3(
			parameters_map['input_schema_name'],
			parameters_map['input_table_or_view_name'],
			parameters_map['aws_credentials_connection_name'],
			parameters_map['s3_output_path']
	)

end

main(json_str)