local luaunit = require("luaunit")
require("./src/execute_exporter")


test_execute_exporter = {}



function test_execute_exporter.test_parse_unused_optional_arguments()
    local args_empty_json_str = '{}'

    args_empty = parse_arguments(args_empty_json_str)
    luaunit.assertNil(args_empty["max_candidates"])
    luaunit.assertNil(args_empty["problem_type"])
    luaunit.assertNil(args_empty["objective"])
    luaunit.assertNotNil(args_empty["compression_type"])


end

function test_execute_exporter.test_parse_used_optional_arguments()
    local args_missing_json_str = '{"max_candidates" : 100, "problem_type" : "regression"}'

    args_missing = parse_arguments(args_missing_json_str)
    luaunit.assertNil(args_missing["max_runtime_for_automl_job_in_seconds"])
    luaunit.assertNil(args_missing["max_runtime_per_training_job_in_seconds"])
    luaunit.assertNotNil(args_missing["max_candidates"])
    luaunit.assertNotNil(args_missing["problem_type"])
    luaunit.assertNil(args_missing["objective"])
    luaunit.assertNotNil(args_missing["compression_type"])
end


function test_execute_exporter.test_parse_invalid_input_string()
    local args_invalid_json_str = '"max_candidates" : 100}'

    args_invalid = parse_arguments(args_invalid_json_str)
    luaunit.assertNil(args_invalid)

end


os.exit(luaunit.LuaUnit.run())