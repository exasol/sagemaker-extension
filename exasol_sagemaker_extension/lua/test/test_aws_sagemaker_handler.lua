local luaunit = require("luaunit")
local mockagne = require("mockagne")
local aws_sagemaker_handler = require("aws_sagemaker_handler")


test_aws_sagemaker_handler = {
    job_name = 'autopilot_job_name',
    query = [[SELECT ::schema."SME_AUTOPILOT_TRAINING_UDF"(
        :job_name ,
        :aws_s3_connection ,
        :aws_region ,
        :role ,
        :s3_bucket_uri,
        :s3_output_path,
        :target_attribute_name ,
        :problem_type ,
        :objective ,
        :total_job_runtime_in_seconds ,
        :max_candidates ,
        :max_runtime_per_training_job_in_seconds
        )]],
    params = {
        schema = 'schema_name',
        job_name = 'job_name',
        aws_s3_connection = 'aws_s3_connection',
        aws_region = 'aws_region',
        role = 'role',
        s3_bucket_uri = 's3_bucket_uri',
        s3_output_path = 's3_output_path',
        target_attribute_name = 'target_attribute_name',
        problem_type = 'problem_type',
        objective = 'objective',
        total_job_runtime_in_seconds = 'total_job_runtime_in_seconds',
        max_candidates = 'max_candidates',
        max_runtime_per_training_job_in_seconds = 'max_runtime_per_training_job_in_seconds'
    }
}

local function mock_pquery_train(exa_mock, query_str, query_params, success, job_name)
    mockagne.when(exa_mock.pquery(query_str, query_params)).thenAnswer(success, job_name)
end

local function mock_error_return_nil(exa_mock)
    mockagne.when(exa_mock.error()).thenAnswer(nil)
end


function  test_aws_sagemaker_handler.setUp()
    exa_mock = mockagne.getMock()
    _G.global_env = exa_mock
    mock_error_return_nil(exa_mock)
end


function test_aws_sagemaker_handler.test_train_autopilot_success()
    mock_pquery_train(
            exa_mock,
            test_aws_sagemaker_handler.query,
            test_aws_sagemaker_handler.params,
            true,
            {{test_aws_sagemaker_handler.job_name}})
    local result = aws_sagemaker_handler.train_autopilot(
            'schema_name',
            'job_name',
            'aws_s3_connection',
            'aws_region',
            'role',
            's3_bucket_uri',
            's3_output_path',
            'target_attribute_name',
            'problem_type',
            'objective',
            'total_job_runtime_in_seconds',
            'max_candidates',
            'max_runtime_per_training_job_in_seconds'
    )
    luaunit.assertEquals(result, test_aws_sagemaker_handler.job_name)

end



os.exit(luaunit.LuaUnit.run())