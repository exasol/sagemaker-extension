local luaunit = require("luaunit")
local mockagne = require("mockagne")
local endpoint_connection_handler = require("src/endpoint_connection_handler")


local endpoint_name = 'endpoint_name'
local status = 'deployed'
local conn_name = [[SME_SAGEMAKER_AUTOPILOT_ENDPOINT_CONNECTION_]] .. endpoint_name
local conn_to = [[TO '{"name":"]] .. endpoint_name .. [[", "status":"]] .. status .. [["}']]

test_endpoint_connection_handler = {
    query = [[CREATE OR REPLACE CONNECTION ]] .. conn_name .. [[ ]] .. conn_to
}

local function mock_pquery_create_conn(exa_mock, query_str, success, result)
    mockagne.when(exa_mock.pquery(query_str, query_params)).thenAnswer(success, result)
end

local function mock_error_return_nil(exa_mock)
    mockagne.when(exa_mock.error()).thenAnswer(nil)
end


function  test_endpoint_connection_handler.setUp()
    exa_mock = mockagne.getMock()
    _G.global_env = exa_mock
    mock_error_return_nil(exa_mock)
end


function test_endpoint_connection_handler.test_delete_autopilot_endpoint_success()
    mock_pquery_create_conn(
            exa_mock,
            test_endpoint_connection_handler.query,
            true,
            nil)
    local result = endpoint_connection_handler.update_model_connection_object(endpoint_name, status)

    luaunit.assertEquals(result, nil)

end



os.exit(luaunit.LuaUnit.run())