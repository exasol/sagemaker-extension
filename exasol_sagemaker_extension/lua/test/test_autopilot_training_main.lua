local luaunit = require("luaunit")
local mockagne = require("mockagne")
require("./src/autopilot_training_main")



test_train_autopilot_main = {
    query = [[SELECT COLUMN_NAME , COLUMN_TYPE FROM SYS.EXA_ALL_COLUMNS eac
					WHERE COLUMN_SCHEMA = :schema_name AND COLUMN_TABLE = :table_name]],
	params = {schema_name='schema_name', table_name='table_name'},
    result = {{'COL1','INTEGER'},{'COL2','VARCHAR(100)'}},
    col_names = 'COL1;COL2',
    col_types = 'INTEGER;VARCHAR(100)'
}


local function mock_error_return_nil(exa_mock)
    mockagne.when(exa_mock.error()).thenAnswer(nil)
end


local function mock_pquery_select(exa_mock, query_str, query_params)
    mockagne.when(exa_mock.pquery(query_str, query_params)).thenAnswer(
            true, test_train_autopilot_main.result)
end

function  test_train_autopilot_main.setUp()
    exa_mock = mockagne.getMock()
    _G.global_env = exa_mock
    mock_error_return_nil(exa_mock)
end


function test_train_autopilot_main.test_parse_unused_optional_arguments()
    local args_empty_json_str = '{}'

    args_empty = parse_arguments(args_empty_json_str)
    luaunit.assertNil(args_empty["max_candidates"])
    luaunit.assertNil(args_empty["problem_type"])
    luaunit.assertNil(args_empty["objective"])
    luaunit.assertNotNil(args_empty["compression_type"])
end

function test_train_autopilot_main.test_parse_used_optional_arguments()
    local args_missing_json_str = '{"max_candidates" : 100, "problem_type" : "regression"}'

    args_missing = parse_arguments(args_missing_json_str)
    luaunit.assertNil(args_missing["max_runtime_for_automl_job_in_seconds"])
    luaunit.assertNil(args_missing["max_runtime_per_training_job_in_seconds"])
    luaunit.assertNotNil(args_missing["max_candidates"])
    luaunit.assertNotNil(args_missing["problem_type"])
    luaunit.assertNil(args_missing["objective"])
    luaunit.assertNotNil(args_missing["compression_type"])
end

function test_train_autopilot_main.test_parse_invalid_input_string()
    local args_invalid_json_str = '"max_candidates" : 100}'

    args_invalid = parse_arguments(args_invalid_json_str)
    luaunit.assertNil(args_invalid["max_candidates"])

end


function test_train_autopilot_main.test_get_table_columns()
    mock_pquery_select(exa_mock, test_train_autopilot_main.query, test_train_autopilot_main.params)
    local col_names, col_types = get_table_columns(
            test_train_autopilot_main.params['schema_name'],
            test_train_autopilot_main.params['table_name'])
    luaunit.assertEquals(col_names, test_train_autopilot_main.col_names)
    luaunit.assertEquals(col_types, test_train_autopilot_main.col_types)
end

os.exit(luaunit.LuaUnit.run())