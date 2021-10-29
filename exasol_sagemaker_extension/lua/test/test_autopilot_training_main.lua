local luaunit = require("luaunit")
local mockagne = require("mockagne")
require("./src/autopilot_training_main")


test_train_autopilot_main = {}


local function mock_error_return_nil(exa_mock)
    mockagne.when(exa_mock.error()).thenAnswer(nil)
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


os.exit(luaunit.LuaUnit.run())