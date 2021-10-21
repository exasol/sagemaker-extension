import importlib_resources


# set deployment paths
BASE_DIR = importlib_resources.files("exasol_sagemaker_extension")
LUA_SRC_DIR = (BASE_DIR / "lua" / "src")

LUA_SRC_MODULE_AUTOPILOT_TRAINING_MAIN_NAME = "autopilot_training_main.lua"
LUA_SRC_MODULE_AWS_S3_HANDLER_NAME = "aws_s3_handler.lua"
LUA_BUNDLED = "bundle_final.lua"

CREATE_STATEMENT_TEMPLATE_AUTOPILOT_TRAINING_LUA_SCRIPT_RESOURCE = BASE_DIR.\
    joinpath("resources").\
    joinpath("create_statement_template_autopilot_training_lua_script.sql")
CREATE_STATEMENT_AUTOPILOT_TRAINING_UDF_RESOURCE = BASE_DIR.\
    joinpath("resources").\
    joinpath("create_statement_autopilot_training_udf.sql")


