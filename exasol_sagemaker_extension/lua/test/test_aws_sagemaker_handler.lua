local luaunit = require("luaunit")
local mockagne = require("mockagne")
local aws_sagemaker_handler = require("./src/aws_sagemaker_handler")


test_aws_sagemaker_handler = {
    job_name = 'autopilot_job_name',
    query_training = [[SELECT AUTOPILOTTRAININGUDF(
        :model_name ,
        :aws_s3_connection ,
        :aws_region ,
        :role ,
        :bucket ,
        :target_attribute_name ,
        :problem_type ,
        :objective ,
        :total_job_runtime_in_seconds ,
        :max_candidates ,
        :max_runtime_per_training_job_in_seconds
        )]],
    params = {
        model_name = 'model_name',
        aws_s3_connection = 'aws_s3_connection',
        aws_region = 'aws_region',
        role = 'role',
        bucket = 'bucket',
        target_attribute_name = 'target_attribute_name',
        problem_type = 'problem_type',
        total_job_runtime_in_seconds = 100,
        max_candidates = 5,
        max_runtime_per_training_job_in_seconds = 10
    }
}

local function mock_pquery_autopilot(exa_mock, query_str, query_params, success, job_name)
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


function test_aws_sagemaker_handler.test_autopilot_training_success()
    mock_pquery_autopilot(exa_mock, M.query_training, M.params, true, M.job_name)
    local sucess, result = aws_sagemaker_handler.autopilot_training()
    luaunit.assertEquals(sucess, true)
    luaunit.assertEquals(result, M.job_name)
end

function test_aws_sagemaker_handler.test_autopilot_training_fail()
    mock_pquery_autopilot(exa_mock, M.query_training, nil, false,nil)
    local sucess, result = aws_sagemaker_handler.autopilot_training()
    luaunit.assertEquals(sucess, false)
end