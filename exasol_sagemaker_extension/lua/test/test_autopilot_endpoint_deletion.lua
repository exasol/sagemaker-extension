local luaunit = require("luaunit")
local mockagne = require("mockagne")
require("autopilot_endpoint_deletion")


test_autopilot_endpoint_deletion = {
    query = [[SELECT ::schema."SME_AUTOPILOT_ENDPOINT_DELETION_UDF"(
		:endpoint_name,
		:aws_s3_connection,
		:aws_region
	)]],
    params = {
		schema='schema_name',
		endpoint_name='endpoint_name',
		aws_s3_connection='aws_s3_connection',
		aws_region='aws_region'
	}
}

local function mock_pquery_train(exa_mock, query_str, query_params, success, result)
    mockagne.when(exa_mock.pquery(query_str, query_params)).thenAnswer(success, result)
end

local function mock_error_return_nil(exa_mock)
    mockagne.when(exa_mock.error()).thenAnswer(nil)
end


function  test_autopilot_endpoint_deletion.setUp()
    exa_mock = mockagne.getMock()
    _G.global_env = exa_mock
    mock_error_return_nil(exa_mock)
end


function test_autopilot_endpoint_deletion.test_delete_autopilot_endpoint_success()
    mock_pquery_train(
            exa_mock,
            test_autopilot_endpoint_deletion.query,
            test_autopilot_endpoint_deletion.params,
            true,
            nil)
    local result = delete_autopilot_endpoint(
            'schema_name',
            'endpoint_name',
            'aws_s3_connection',
            'aws_region'
    )
    luaunit.assertEquals(result, nil)

end


os.exit(luaunit.LuaUnit.run())