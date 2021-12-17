local luaunit = require("luaunit")
local mockagne = require("mockagne")
require("autopilot_endpoint_deployment")


test_autopilot_endpoint_deployment = {
    endpoint_name = 'endpoint_name',
    query =  [[SELECT ::schema."SME_AUTOPILOT_ENDPOINT_DEPLOYMENT_UDF"(
		:job_name,
		:endpoint_name,
		:instance_type,
		:instance_count,
		:aws_s3_connection,
		:aws_region
	)]],
    params = {
		schema='schema_name',
		job_name='job_name',
		endpoint_name='endpoint_name',
		instance_type='instance_type',
		instance_count='instance_count',
		aws_s3_connection='aws_s3_connection',
		aws_region='aws_region'
	}
}

local function mock_pquery_select(exa_mock, query_str, query_params, success, result)
    mockagne.when(exa_mock.pquery(query_str, query_params)).thenAnswer(success, result)
end

local function mock_error_return_nil(exa_mock)
    mockagne.when(exa_mock.error()).thenAnswer(nil)
end


function  test_autopilot_endpoint_deployment.setUp()
    exa_mock = mockagne.getMock()
    _G.global_env = exa_mock
    mock_error_return_nil(exa_mock)
end


function test_autopilot_endpoint_deployment.test_poll_autopilot_job_status()
    mock_pquery_select(
            exa_mock,
            test_autopilot_endpoint_deployment.query,
            test_autopilot_endpoint_deployment.params,
            true,
            {{test_autopilot_endpoint_deployment.endpoint_name}})
    local result  = deploy_autopilot_endpoint(
            'schema_name',
            'job_name',
            'endpoint_name',
            'instance_type',
            'instance_count',
            'aws_s3_connection','aws_region')
    luaunit.assertEquals(result, test_autopilot_endpoint_deployment.endpoint_name)
end



os.exit(luaunit.LuaUnit.run())