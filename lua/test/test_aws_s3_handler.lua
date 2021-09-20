local luaunit = require("luaunit")
local aws_s3_handler = require("./src/aws_s3_handler")


test_aws_s3_handler = {
    schema_name = 'TEST_SCHEMA',
    table_name = 'TEST_TABLE',
    connection_name = 'TEST_CONNECTION',
    s3_output_path = '/test_path/'
}

local function mock_pquery_incorrect(...)
    return false, {}
end

local function mock_pquery_correct(...)
    return true, {{1}}
end

local function mock_pquery_incorrect_node_count(...)
    return true, {}
end

local function mock_pquery_incorrect_export(...)
    local args = {...}
    if args[1]:find('EXPORT') then
        return false, {{1}}
    else
        return true, {{1}}
    end
end

local function get_table_size(t)
    local count = 0
    for k, v in pairs(t) do
        count = count + 1
    end
    return count
end

local function mock_exit_func()
    return nil
end


aws_s3_handler.exit_func = mock_exit_func

function test_aws_s3_handler.test_get_node_count_returns_true()
    aws_s3_handler.pquery_func = mock_pquery_correct
    local res = aws_s3_handler.get_node_count()
    luaunit.assertNotNil(res)
    luaunit.assertEquals(res, 1)
end

function test_aws_s3_handler.test_get_node_count_returns_false()
    aws_s3_handler.pquery_func = mock_pquery_incorrect
    local res = aws_s3_handler.get_node_count()
    luaunit.assertNil(res)
end

function test_aws_s3_handler.test_get_node_count_returns_wrong()
    aws_s3_handler.pquery_func = mock_pquery_incorrect_node_count
    local res = aws_s3_handler.get_node_count()
    luaunit.assertNil(res)
end



function test_aws_s3_handler.test_prepare_export_query()
    for i=1,5 do
        local n_nodes = math.random(1, 20)
        local n_exporter = n_nodes * aws_s3_handler.parallelism_factor


        local export_query, params = aws_s3_handler.prepare_export_query(
                n_nodes,
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
        luaunit.assertEquals(params["t"], test_aws_s3_handler.schema_name..'.'..test_aws_s3_handler.table_name)
        luaunit.assertEquals(get_table_size(params), n_exporter + 2)
    end
end


function test_aws_s3_handler.test_export_to_s3_returns_true()
    aws_s3_handler.pquery_func = mock_pquery_correct
    local res = aws_s3_handler.export_to_s3(
            test_aws_s3_handler.schema_name,
            test_aws_s3_handler.table_name,
            test_aws_s3_handler.connection_name,
            test_aws_s3_handler.s3_output_path)
    luaunit.assertEquals(res, true)
end

function test_aws_s3_handler.test_export_to_s3_returns_false()
    aws_s3_handler.pquery_func = mock_pquery_incorrect_export
    local res = aws_s3_handler.export_to_s3(
            test_aws_s3_handler.schema_name,
            test_aws_s3_handler.table_name,
            test_aws_s3_handler.connection_name,
            test_aws_s3_handler.s3_output_path)
    luaunit.assertEquals(res, false)

end

os.exit(luaunit.LuaUnit.run())