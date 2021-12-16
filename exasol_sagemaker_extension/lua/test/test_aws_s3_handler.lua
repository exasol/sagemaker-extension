local luaunit = require("luaunit")
local mockagne = require("mockagne")
local aws_s3_handler = require("aws_s3_handler")


test_aws_s3_handler = {
    schema_name = 'TEST_SCHEMA',
    table_name = 'TEST_TABLE',
    connection_name = 'TEST_CONNECTION',
    s3_output_path = '/test_path/'
}


local function get_table_size(t)
    local count = 0
    for _ , _ in pairs(t) do
        count = count + 1
    end
    return count
end



local function mock_pquery_nproc(exa_mock, success, ret)
    mockagne.when(exa_mock.pquery([[SELECT NPROC()]])).thenAnswer(success, ret)
end

local function mock_pquery_export(exa_mock, query_str, query_params, success)
    mockagne.when(exa_mock.pquery(query_str, query_params)).thenAnswer(success, _)
end

local function mock_error_return_nil(exa_mock)
    mockagne.when(exa_mock.error()).thenAnswer(nil)
end




function  test_aws_s3_handler.setUp()
    exa_mock = mockagne.getMock()
    _G.global_env = exa_mock
    mock_error_return_nil(exa_mock)
end


function test_aws_s3_handler.test_get_node_count_returns_true()
    local n_nodes = 10
    mock_pquery_nproc(exa_mock, true, {{n_nodes}})
    local res = aws_s3_handler.get_node_count()
    luaunit.assertNotNil(res)
    luaunit.assertEquals(res, n_nodes)
end

function test_aws_s3_handler.test_get_node_count_returns_false()
    local n_nodes = 20
    mock_pquery_nproc(exa_mock, false, {{n_nodes}})
    local res = aws_s3_handler.get_node_count()
    luaunit.assertNil(res)
end


function test_aws_s3_handler.test_get_node_count_returns_wrong()
    mock_pquery_nproc(exa_mock, false, {{}})
    local res = aws_s3_handler.get_node_count()
    luaunit.assertNil(res)
end

function test_aws_s3_handler.test_prepare_export_query()
    local parallelism_factor = 1
    for _ = 1, 5 do
        local n_nodes = math.random(1, 20)
        local n_exporter = n_nodes * parallelism_factor

        local export_query, params = aws_s3_handler.prepare_export_query(
                n_nodes,
                parallelism_factor,
                test_aws_s3_handler.schema_name,
                test_aws_s3_handler.table_name,
                test_aws_s3_handler.connection_name,
                test_aws_s3_handler.s3_output_path)

        -- check export query string
        local keyword = 'INTO CSV AT'
        luaunit.assertNotNil(string.find(export_query, keyword))
        local file_part = export_query:sub(string.find(export_query, keyword) + keyword:len())
        local _, n_files = file_part:gsub(" FILE ", "")
        luaunit.assertEquals(n_files,  n_exporter)

        -- check query parameters
        luaunit.assertEquals(params["c"], test_aws_s3_handler.connection_name)
        luaunit.assertEquals(params["t"], test_aws_s3_handler.schema_name .. '.' .. test_aws_s3_handler.table_name)
        luaunit.assertEquals(get_table_size(params), n_exporter + 2)
    end
end


function test_aws_s3_handler.test_export_to_s3_with_correct_node_count()
    local parallelism_factor = aws_s3_handler.default_parallelism_factor
    local n_nodes = 30
    mock_error_return_nil(exa_mock)
    local export_query, params = aws_s3_handler.prepare_export_query(
        n_nodes,
        parallelism_factor,
        test_aws_s3_handler.schema_name,
        test_aws_s3_handler.table_name,
        test_aws_s3_handler.connection_name,
        test_aws_s3_handler.s3_output_path)

    mock_pquery_nproc(exa_mock, true, {{n_nodes}})
    for _, success in ipairs({true, false}) do
        mock_pquery_export(exa_mock, export_query, params, success)
        local res = aws_s3_handler.export_to_s3(
                test_aws_s3_handler.schema_name,
                test_aws_s3_handler.table_name,
                test_aws_s3_handler.connection_name,
                test_aws_s3_handler.s3_output_path)
        luaunit.assertEquals(res, nil)
    end
end



os.exit(luaunit.LuaUnit.run())