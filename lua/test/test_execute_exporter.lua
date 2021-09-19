local luaunit = require("luaunit")
require("./src/execute_exporter")


test_execute_exporter = {}

function test_execute_exporter.test_parse_optional_arguments()
    local args_empty_json_str = '{}'
    local args_missing_json_str  =  '{"max_candidates" : 100, "problem_type" : "regression"}'

    -- check whether optional args are added
    args_empty = parse_arguments(args_empty_json_str)
    luaunit.assertNil(args_empty["max_candidates"])
    luaunit.assertNil(args_empty["problem_type"])
    luaunit.assertNil(args_empty["objective"])
    luaunit.assertNotNil(args_empty["compression_type"])

    -- check wheter optinal added args are not nil
    args_missing = parse_arguments(args_missing_json_str)
    luaunit.assertNil(args_missing["max_runtime_for_automl_job_in_seconds"])
    luaunit.assertNil(args_missing["max_runtime_per_training_job_in_seconds"])
    luaunit.assertNotNil(args_missing["max_candidates"])
    luaunit.assertNotNil(args_missing["problem_type"])
    luaunit.assertNil(args_missing["objective"])
    luaunit.assertNotNil(args_missing["compression_type"])
    
end



os.exit(luaunit.LuaUnit.run())