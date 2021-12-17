local luaunit = require("luaunit")
local mockagne = require("mockagne")
require("autopilot_job_status_polling")


test_autopilot_job_status_polling = {
    job_status = 'job_status',
    job_secondary_status = 'job_secondary_status',
    query = [[SELECT ::schema."SME_AUTOPILOT_JOB_STATUS_POLLING_UDF"(
		:job_name,
		:aws_s3_connection,
		:aws_region
	)]],
    params = {
		schema='schema_name',
		job_name='job_name',
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


function  test_autopilot_job_status_polling.setUp()
    exa_mock = mockagne.getMock()
    _G.global_env = exa_mock
    mock_error_return_nil(exa_mock)
end


function test_autopilot_job_status_polling.test_poll_autopilot_job_status()
    mock_pquery_train(
            exa_mock,
            test_autopilot_job_status_polling.query,
            test_autopilot_job_status_polling.params,
            true,
            {{test_autopilot_job_status_polling.job_status, test_autopilot_job_status_polling.job_secondary_status}})
    local summary, _ = poll_autopilot_job_status(
            'schema_name',
            'job_name',
            'aws_s3_connection',
            'aws_region'
    )
    luaunit.assertEquals(summary[1][1], test_autopilot_job_status_polling.job_status)
    luaunit.assertEquals(summary[1][2], test_autopilot_job_status_polling.job_secondary_status)

end



os.exit(luaunit.LuaUnit.run())