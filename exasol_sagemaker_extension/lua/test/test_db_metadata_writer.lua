local luaunit = require("luaunit")
local mockagne = require("mockagne")
local db_metadata_writer = require("db_metadata_writer")


test_db_metadata_writer = {
     query = [[INSERT INTO ::schema."SME_METADATA_AUTOPILOT_JOBS" VALUES(
			CURRENT_TIMESTAMP,
			:job_name,
			:aws_credentials_connection_name,
			:iam_sagemaker_role,
			:s3_bucket_uri,
			:s3_output_path,
			:target_attribute_name,
			:problem_type,
			:objective,
			:max_runtime_for_automl_job_in_seconds,
			:max_candidates,
			:max_runtime_per_training_job_in_seconds,
			:session_id,
			:script_user,
			:col_names,
			:col_types
        )]],

    params = {
        schema = 'schema_name',
		job_name='job_name',
		aws_credentials_connection_name='aws_credentials_connection_name',
		iam_sagemaker_role='iam_sagemaker_role',
		s3_bucket_uri='s3_bucket_uri',
		s3_output_path='s3_output_path',
		target_attribute_name='target_attribute_name',
		problem_type='problem_type',
		objective='objective',
		max_runtime_for_automl_job_in_seconds='max_runtime_for_automl_job_in_seconds',
		max_candidates='max_candidates',
		max_runtime_per_training_job_in_seconds='max_runtime_per_training_job_in_seconds',
		session_id='session_id',
		script_user='script_user',
		col_names='col_names',
		col_types='col_types'
    }

}

local function mock_pquery_insert(exa_mock, query_str, query_params)
    mockagne.when(exa_mock.pquery(query_str, query_params)).thenAnswer(true, _)
end

local function mock_error_return_nil(exa_mock)
    mockagne.when(exa_mock.error()).thenAnswer(nil)
end


function  test_db_metadata_writer.setUp()
    exa_mock = mockagne.getMock()
    _G.global_env = exa_mock
    mock_error_return_nil(exa_mock)
end


function test_db_metadata_writer.test_insert_metadata_into_db_success()
	mock_pquery_insert(exa_mock, test_db_metadata_writer.query, test_db_metadata_writer.params)
    local result = db_metadata_writer.insert_metadata_into_db(
            'schema_name',
			'job_name',
			'aws_credentials_connection_name',
			'iam_sagemaker_role',
			's3_bucket_uri',
			's3_output_path',
			'target_attribute_name',
			'problem_type',
			'objective',
			'max_runtime_for_automl_job_in_seconds',
			'max_candidates',
			'max_runtime_per_training_job_in_seconds',
			'session_id',
			'script_user',
			'col_names',
			'col_types')
    luaunit.assertEquals(result, nil)
end


os.exit(luaunit.LuaUnit.run())