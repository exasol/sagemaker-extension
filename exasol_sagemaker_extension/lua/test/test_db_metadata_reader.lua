local luaunit = require("luaunit")
local mockagne = require("mockagne")
local db_metadata_reader = require("db_metadata_reader")


test_db_metadata_reader = {
	params = {
		schema='schema',
		job_name='job_name'
	}
}

local function get_select_all_query()
	return [[SELECT * FROM ]]
			.. [[::schema]]
			.. [[."SME_METADATA_AUTOPILOT_JOBS" WHERE JOB_NAME = ]]
			.. [[:job_name]]
end

local function mock_pquery_select(exa_mock, query_str, params, result)
    mockagne.when(exa_mock.pquery(query_str, params)).thenAnswer(true, result)
end

local function mock_error_return_nil(exa_mock)
    mockagne.when(exa_mock.error()).thenAnswer(nil)
end


function  test_db_metadata_reader.setUp()
    exa_mock = mockagne.getMock()
    _G.global_env = exa_mock
    mock_error_return_nil(exa_mock)
end


function test_db_metadata_reader.test_read_metadata()
	local query_result = {'VAL_1', 'VAL_2', 'VAL_3'}
	mock_pquery_select(exa_mock, get_select_all_query(),
			test_db_metadata_reader.params, query_result)
    local result = db_metadata_reader.read_metadata(
			test_db_metadata_reader.params.schema,
			test_db_metadata_reader.params.job_name,
			nil
	)
	luaunit.assertEquals(query_result, result)

end


os.exit(luaunit.LuaUnit.run())