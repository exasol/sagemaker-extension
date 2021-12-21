local json = require('cjson')
local luaunit = require("luaunit")
local mockagne = require("mockagne")
local endpoint_connection_handler = require("endpoint_connection_handler")


local aws_s3_connection = 'aws_s3_connection'
local aws_region = 'eu-central-1'
local endpoint_name = 'endpoint_name'
local status = 'deployed'
local conn_data_dict = {
    aws_s3_connection=aws_s3_connection,
    aws_region = aws_region,
    endpoint_name=endpoint_name,
    status=status,
    batch_size=100
}

local conn_name = [[SME_SAGEMAKER_AUTOPILOT_ENDPOINT_CONNECTION_]] .. string.upper(endpoint_name)
local conn_to = json.encode(conn_data_dict)

test_endpoint_connection_handler = {
    query = [[CREATE OR REPLACE CONNECTION ]] .. conn_name .. [[ TO ']] .. conn_to .. [[']]
}

local function mock_pquery_create_conn(exa_mock, query_str, success, result)
    mockagne.when(exa_mock.pquery(query_str)).thenAnswer(success, result)
end

local function mock_error_return_nil(exa_mock)
    mockagne.when(exa_mock.error()).thenAnswer(nil)
end


function  test_endpoint_connection_handler.setUp()
    exa_mock = mockagne.getMock()
    _G.global_env = exa_mock
    mock_error_return_nil(exa_mock)
end


function test_endpoint_connection_handler.test_update_autopilot_endpoint_success()
    mock_pquery_create_conn(
            exa_mock,
            test_endpoint_connection_handler.query,
            true,
            nil)
    local result = endpoint_connection_handler.update_model_connection_object(
            aws_s3_connection, aws_region, endpoint_name, status)

    luaunit.assertNotNil(result)

end



os.exit(luaunit.LuaUnit.run())